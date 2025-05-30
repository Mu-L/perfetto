// Copyright (C) 2024 The Android Open Source Project
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import {Time} from '../../base/time';
import {DatasetSliceTrack} from '../../components/tracks/dataset_slice_track';
import {Trace} from '../../public/trace';
import {SourceDataset} from '../../trace_processor/dataset';
import {LONG, NUM, STR} from '../../trace_processor/query_result';
import {
  HeapProfileFlamegraphDetailsPanel,
  profileType,
} from './heap_profile_details_panel';

export function createHeapProfileTrack(
  trace: Trace,
  uri: string,
  tableName: string,
  upid: number,
  heapProfileIsIncomplete: boolean,
) {
  return new DatasetSliceTrack({
    trace,
    uri,
    dataset: new SourceDataset({
      src: tableName,
      schema: {
        ts: LONG,
        type: STR,
        id: NUM,
      },
      filter: {
        col: 'upid',
        eq: upid,
      },
    }),
    detailsPanel: (row) => {
      const ts = Time.fromRaw(row.ts);
      const type = profileType(row.type);
      return new HeapProfileFlamegraphDetailsPanel(
        trace,
        heapProfileIsIncomplete,
        upid,
        type,
        ts,
      );
    },
    tooltip: (slice) => slice.row.type,
  });
}
