/*
 * Copyright (C) 2025 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef SRC_PROTOVM_SLAB_ALLOCATOR_H_
#define SRC_PROTOVM_SLAB_ALLOCATOR_H_

#include <algorithm>
#include <cstdlib>

#include <sys/mman.h>

#include "perfetto/base/logging.h"
#include "perfetto/ext/base/flat_hash_map.h"
#include "perfetto/ext/base/utils.h"
#include "src/base/intrusive_list.h"

// An efficient allocator for elements with fixed size and alignment
// requirements.
//
// Design doc: go/perfetto-protovm-implementation
//
// Key features:
//
// - Slab allocation: Instead of requesting memory for each individual element,
// this allocator pre-allocates large memory chunks (slabs). Each slab is
// designed to hold multiple elements.
//
// - Element free list: A free list tracks available elements within each
// individual slab, allowing for O(1) access time during allocation.
//
// - Slab free lists: Slabs are managed within one of two intrusive lists. The
// "non-full slabs" list and the "full slabs" list. This organization allows
// "non-full" slabs (those with available space for new allocations) to be
// accessed in O(1) time.
//
// - Block-to-Slab hash map: A hash map links 4KB-aligned memory blocks to their
// corresponding slab. This enables O(1) mapping of an element back to its slab
// during deallocation.

namespace perfetto {
namespace protovm {

namespace internal {
static constexpr size_t k4KiloBytes = static_cast<size_t>(4) * 1024;
}

inline size_t RoundUpToSysPageSize(size_t req_size) {
  const size_t page_size = base::GetSysPageSize();
  return (req_size + page_size - 1) & ~(page_size - 1);
}

template <size_t ElementSize, size_t ElementAlign, size_t SlabCapacity = 64>
class Slab {
 public:
  struct IntrusiveListTraits {
    static constexpr size_t NodeOffset() {
      return offsetof(Slab, intrusive_list_node_);
    }
  };

  static Slab* New() {
    size_t rounded_up_size = RoundUpToSysPageSize(sizeof(Slab));
    PERFETTO_CHECK(rounded_up_size >= sizeof(Slab));
    void* ptr = mmap(nullptr, rounded_up_size, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (ptr == MAP_FAILED) {
      return nullptr;
    }

    // Expect allocated page to be always 4KB-aligned
    PERFETTO_CHECK(ptr);
    PERFETTO_CHECK(
        (reinterpret_cast<uintptr_t>(ptr) & (internal::k4KiloBytes - 1)) == 0);

    new (ptr) Slab{};

    return static_cast<Slab*>(ptr);
  }

  static void Delete(Slab* slab) {
    slab->~Slab();

    const size_t rounded_up_size =
        RoundUpToSysPageSize(sizeof(Slot[SlabCapacity]));
    int res = munmap(slab, rounded_up_size);
    PERFETTO_CHECK(res == 0);
  }

  Slab(const Slab&) = delete;
  Slab& operator=(const Slab&) = delete;

  Slab() {
    next_free_slot_ = &slots_[0];

    for (size_t i = 0; i + 1 < SlabCapacity; ++i) {
      auto& slot = slots_[i];
      auto& next_slot = slots_[i + 1];
      slot.next = &next_slot;
    }

    auto& last_slot = slots_[SlabCapacity - 1];
    last_slot.next = nullptr;
  }

  Slab(Slab&& other)
      : slots_{std::move(other.slots_)},
        next_free_slot_{other.next_free_slot_},
        size_{other.size_} {}

  void* Allocate() {
    PERFETTO_DCHECK(next_free_slot_);
    auto* slot = next_free_slot_;
    next_free_slot_ = next_free_slot_->next;
    ++size_;
    return slot;
  }

  void Free(void* p) {
    auto* slot = static_cast<Slot*>(p);
    PERFETTO_DCHECK(slot >= &slots_[0] && slot <= &slots_[SlabCapacity]);
    slot->next = next_free_slot_;
    next_free_slot_ = slot;
    --size_;
  }

  bool IsFull() const { return size_ == SlabCapacity; }

  bool IsEmpty() const { return size_ == 0; }

  const void* GetBeginAddress() const { return this; }

  const void* GetEndAddress() const {
    return reinterpret_cast<const void*>(reinterpret_cast<uintptr_t>(this) +
                                         sizeof(Slab));
  }

 private:
  union Slot {
    Slot* next;
    alignas(ElementAlign) unsigned char element[ElementSize];
  };

  Slot* next_free_slot_{nullptr};
  std::size_t size_{0};
  base::IntrusiveListNode intrusive_list_node_;
  Slot slots_[SlabCapacity];
};

template <size_t ElementSize, size_t ElementAlign, size_t Blocks4KBPerSlab = 1>
class SlabAllocator {
 public:
  ~SlabAllocator() {
    DeleteSlabs(slabs_non_full_);
    DeleteSlabs(slabs_full_);
  }

  void* Allocate() {
    // Create new slab if needed
    if (slabs_non_full_.Empty()) {
      auto* slab = SlabType::New();
      if (!slab) {
        return nullptr;
      }
      slabs_non_full_.PushFront(*slab);
      InsertHashMapEntries(*slab);
    }

    // Allocate using any non-full slab
    auto& slab = slabs_non_full_.Front();
    auto* allocated = slab.Allocate();
    PERFETTO_CHECK(allocated);

    // Move to "full slabs" list if needed
    if (slab.IsFull()) {
      slabs_non_full_.Erase(slab);
      slabs_full_.PushFront(slab);
    }

    return allocated;
  }

  void Free(void* p) {
    auto& slab = FindSlabInHashMap(p);

    // Move to "non-full slabs" list if needed
    if (slab.IsFull()) {
      slabs_full_.Erase(slab);
      slabs_non_full_.PushFront(slab);
    }

    slab.Free(p);

    // Deallocate the slab if it becomes empty and it's not the sole non-full
    // slab.
    //
    // The "is not the sole non-full slab" condition avoids thrashing scenarios
    // where a slab is repeatedly allocated and deallocated. For example:
    // 1. Allocate element x -> a new slab is allocated.
    // 2. Free element x -> slab becomes empty and is deallocated.
    // 3. Allocate element y -> a new slab is allocated again.
    // 4. Free element y -> slab becomes empty and is deallocated again.
    if (slab.IsEmpty() && slabs_non_full_.Size() > 1) {
      EraseHashMapEntries(slab);
      slabs_non_full_.Erase(slab);
      SlabType::Delete(&slab);
    }
  }

 private:
  // Calculate slab capacity (number of elements) to optimize memory usage (slab
  // size is a multiple of 4KB)
  static constexpr size_t SlabOverhead =
      sizeof(Slab<ElementSize, ElementAlign, 1>) -
      (sizeof(Slab<ElementSize, ElementAlign, 2>) -
       sizeof(Slab<ElementSize, ElementAlign, 1>));
  static constexpr size_t MemoryAvailableForElementsInSlab =
      Blocks4KBPerSlab * internal::k4KiloBytes - SlabOverhead;
  static_assert(sizeof(ElementSize) <= MemoryAvailableForElementsInSlab,
                "Cannot fit element into the spefified number of 4KB memory "
                "blocks per slab. Please increase the number.");
  static constexpr size_t SlabCapacity =
      MemoryAvailableForElementsInSlab / sizeof(ElementSize);

  using SlabType = Slab<ElementSize, ElementAlign, SlabCapacity>;

  static_assert(alignof(SlabType) <= internal::k4KiloBytes,
                "SlabAllocator currently supports alignment <= 4KB");

  void InsertHashMapEntries(SlabType& slab) {
    for (auto p = reinterpret_cast<uintptr_t>(slab.GetBeginAddress());
         p < reinterpret_cast<uintptr_t>(slab.GetEndAddress());
         p += internal::k4KiloBytes) {
      PERFETTO_DCHECK(p % internal::k4KiloBytes == 0);
      block_4KB_aligned_to_slab_.Insert(p, &slab);
    }
  }

  void EraseHashMapEntries(const SlabType& slab) {
    for (auto p = reinterpret_cast<uintptr_t>(slab.GetBeginAddress());
         p < reinterpret_cast<uintptr_t>(slab.GetEndAddress());
         p += internal::k4KiloBytes) {
      PERFETTO_DCHECK(p % internal::k4KiloBytes == 0);
      block_4KB_aligned_to_slab_.Erase(p);
    }
  }

  SlabType& FindSlabInHashMap(const void* ptr) {
    auto ptr_4KB_aligned = reinterpret_cast<uintptr_t>(ptr) &
                           ~(static_cast<uintptr_t>(internal::k4KiloBytes) - 1);
    SlabType** slab = block_4KB_aligned_to_slab_.Find(ptr_4KB_aligned);
    PERFETTO_CHECK(slab);
    PERFETTO_CHECK(*slab);
    return **slab;
  }

  void DeleteSlabs(
      base::IntrusiveList<SlabType, typename SlabType::IntrusiveListTraits>&
          slabs) {
    while (!slabs.Empty()) {
      auto& slab = slabs.Front();
      slabs.PopFront();
      SlabType::Delete(&slab);
    }
  }

  base::FlatHashMap<uintptr_t, SlabType*> block_4KB_aligned_to_slab_;
  base::IntrusiveList<SlabType, typename SlabType::IntrusiveListTraits>
      slabs_non_full_;
  base::IntrusiveList<SlabType, typename SlabType::IntrusiveListTraits>
      slabs_full_;
};

}  // namespace protovm
}  // namespace perfetto

#endif  // SRC_PROTOVM_SLAB_ALLOCATOR_H_
