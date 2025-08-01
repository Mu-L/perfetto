/*
 * Copyright (C) 2023 The Android Open Source Project
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

#ifndef SRC_TRACE_PROCESSOR_IMPORTERS_FTRACE_PKVM_HYP_CPU_TRACKER_H_
#define SRC_TRACE_PROCESSOR_IMPORTERS_FTRACE_PKVM_HYP_CPU_TRACKER_H_

#include "perfetto/ext/base/string_view.h"
#include "perfetto/protozero/field.h"
#include "src/trace_processor/storage/trace_storage.h"

namespace perfetto {
namespace trace_processor {

class TraceProcessorContext;

// Handles parsing and showing hypervisor events in the UI.
// TODO(b/249050813): link to the documentation once it's available in AOSP.
class PkvmHypervisorCpuTracker {
 public:
  explicit PkvmHypervisorCpuTracker(TraceProcessorContext*);

  static bool IsPkvmHypervisorEvent(uint32_t /*event_id*/);

  void ParseHypEvent(uint32_t cput,
                     int64_t timestamp,
                     uint32_t event_id,
                     protozero::ConstBytes blob);

 private:
  void ParseHypEnter(uint32_t cpu, int64_t timestamp);
  void ParseHypExit(uint32_t cpu, int64_t timestamp);
  void ParseHostHcall(uint32_t cpu, protozero::ConstBytes blob);
  void ParseHostSmc(uint32_t cpu, protozero::ConstBytes blob);
  void ParseHostMemAbort(uint32_t cpu, protozero::ConstBytes blob);
  void ParseHostFfaCall(uint32_t cpu, protozero::ConstBytes blob);
  void ParseIommuIdmap(uint32_t cpu, protozero::ConstBytes blob);
  void ParsePsciMemProtect(uint32_t cpu, protozero::ConstBytes blob);
  void ParseIommuIdmapComplete(uint32_t cpu, protozero::ConstBytes blob);
  void ParseVcuIllegalTrap(uint32_t cpu, protozero::ConstBytes blob);

  TraceProcessorContext* context_;
  const StringId category_;
  const StringId slice_name_;
  const StringId hyp_enter_reason_;
  const StringId func_id_;
  const StringId handled_;
  const StringId err_;
  const StringId host_ffa_call_;
  const StringId iommu_idmap_;
  const StringId from_;
  const StringId to_;
  const StringId prot_;
  const StringId psci_mem_protect_;
  const StringId count_;
  const StringId was_;
  const StringId iommu_idmap_complete_;
  const StringId map_;
  const StringId vcpu_illegal_trap_;
  const StringId esr_;
  const StringId host_hcall_;
  const StringId id_;
  const StringId invalid_;
  const StringId host_smc_;
  const StringId forwarded_;
  const StringId host_mem_abort_;
  const StringId addr_;
};

}  // namespace trace_processor
}  // namespace perfetto

#endif  // SRC_TRACE_PROCESSOR_IMPORTERS_FTRACE_PKVM_HYP_CPU_TRACKER_H_
