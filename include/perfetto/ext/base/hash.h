/*
 * Copyright (C) 2019 The Android Open Source Project
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

#ifndef INCLUDE_PERFETTO_EXT_BASE_HASH_H_
#define INCLUDE_PERFETTO_EXT_BASE_HASH_H_

#include <cstddef>

namespace perfetto::base {

// This is for using already-hashed key into std::unordered_map and avoid the
// cost of re-hashing. Example:
// unordered_map<uint64_t, Value, AlreadyHashed> my_map.
template <typename T>
struct AlreadyHashed {
  size_t operator()(const T& x) const { return static_cast<size_t>(x); }
};

}  // namespace perfetto::base

#endif  // INCLUDE_PERFETTO_EXT_BASE_HASH_H_
