/*
 * Copyright (C) 2024 The Android Open Source Project
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

#ifndef SRC_TRACE_PROCESSOR_PERFETTO_SQL_ENGINE_DATAFRAME_STORAGE_MODULE_H_
#define SRC_TRACE_PROCESSOR_PERFETTO_SQL_ENGINE_DATAFRAME_STORAGE_MODULE_H_

#include <cstddef>
#include <memory>
#include <string>
#include <string_view>
#include <variant>
#include <vector>

#include "perfetto/base/logging.h"
#include "perfetto/base/status.h"
#include "src/trace_processor/dataframe/dataframe.h"
#include "src/trace_processor/sqlite/bindings/sqlite_module.h"
#include "src/trace_processor/sqlite/bindings/sqlite_result.h"
#include "src/trace_processor/sqlite/bindings/sqlite_type.h"
#include "src/trace_processor/sqlite/bindings/sqlite_value.h"
#include "src/trace_processor/sqlite/sqlite_utils.h"

namespace perfetto::trace_processor {

// TODO
struct DataframeStorageModule : sqlite::Module<DataframeStorageModule> {
  static constexpr auto kType = kCreateOnly;
  static constexpr bool kSupportsWrites = true;
  static constexpr bool kDoesOverloadFunctions = false;

  using SharedDataframe = std::shared_ptr<dataframe::Dataframe>;
  using StaticDataframe = dataframe::Dataframe*;
  using DataframeVariant = std::variant<SharedDataframe, StaticDataframe>;

  struct TaggedDataframe {
    DataframeVariant df_variant;
    std::string name;
    int savepoint_version;
    bool is_deleted = false;
  };
  struct Context {
    TaggedDataframe* GetMaxVersionDataframe(std::string_view name) {
      TaggedDataframe* it = nullptr;
      for (auto& df : tagged_dataframes) {
        if (df.name != name) {
          continue;
        }
        if (!it || df.savepoint_version > it->savepoint_version) {
          it = &df;
        }
      }
      return it;
    }
    std::vector<TaggedDataframe> tagged_dataframes;
  };
  struct Vtab : sqlite::Module<DataframeStorageModule>::Vtab {
    Context* ctx = nullptr;
    int savepoint_version;
  };
  struct Cursor : sqlite::Module<DataframeStorageModule>::Cursor {};

  static int Create(sqlite3* db,
                    void* raw_ctx,
                    int argc,
                    const char* const* argv,
                    sqlite3_vtab** vtab,
                    char** err) {
    PERFETTO_CHECK(argc == 3);

    std::string_view name = argv[2];
    if (name != "__intrinsic_dataframe_storage") {
      *err = sqlite3_mprintf(
          "dataframe storage table name must be __intrinsic_dataframe_storage");
      return SQLITE_ERROR;
    }
    static constexpr char kCreateTable[] = R"(
      CREATE TABLE x(
        name TEXT,
        value BLOB,
        PRIMARY KEY(name)
      ) WITHOUT ROWID;
    )";
    if (int r = sqlite3_declare_vtab(db, kCreateTable); r != SQLITE_OK) {
      return r;
    }
    auto t = std::make_unique<Vtab>();
    t->ctx = GetContext(raw_ctx);
    *vtab = t.release();
    return SQLITE_OK;
  }
  static int Destroy(sqlite3_vtab* vtab) {
    std::unique_ptr<Vtab> v(GetVtab(vtab));
    return SQLITE_OK;
  }
  static int Connect(sqlite3* db,
                     void* raw_ctx,
                     int argc,
                     const char* const* argv,
                     sqlite3_vtab** vtab,
                     char** err) {
    return Create(db, raw_ctx, argc, argv, vtab, err);
  }
  static int Disconnect(sqlite3_vtab* vtab) {
    std::unique_ptr<Vtab> v(GetVtab(vtab));
    return SQLITE_OK;
  }

  static int BestIndex(sqlite3_vtab*, sqlite3_index_info*) {
    return SQLITE_OK;
  }
  static int Open(sqlite3_vtab*, sqlite3_vtab_cursor**) { return SQLITE_ERROR; }
  static int Close(sqlite3_vtab_cursor*) { return SQLITE_ERROR; }
  static int Filter(sqlite3_vtab_cursor*,
                    int,
                    const char*,
                    int,
                    sqlite3_value**) {
    return SQLITE_ERROR;
  }
  static int Next(sqlite3_vtab_cursor*) { return SQLITE_ERROR; }
  static int Eof(sqlite3_vtab_cursor*) { return SQLITE_ERROR; }
  static int Column(sqlite3_vtab_cursor*, sqlite3_context*, int) {
    return SQLITE_ERROR;
  }
  static int Rowid(sqlite3_vtab_cursor*, sqlite_int64*) { return SQLITE_ERROR; }

  static int Update(sqlite3_vtab* t,
                    int argc,
                    sqlite3_value** argv,
                    sqlite_int64*) {
    auto* v = GetVtab(t);
    if (argc == 1) {
      // DELETE
      const char* name = sqlite::value::Text(argv[0]);
      TaggedDataframe* it = v->ctx->GetMaxVersionDataframe(name);
      if (!it || it->is_deleted) {
        return sqlite::utils::SetError(
            t, base::ErrStatus("no such dataframe %s", name));
      }
      it->is_deleted = true;
      return SQLITE_OK;
    }
    if (sqlite::value::Type(argv[0]) == sqlite::Type::kNull) {
      // INSERT
      const char* name = sqlite::value::Text(argv[2]);
      TaggedDataframe* it = v->ctx->GetMaxVersionDataframe(name);
      if (it && !it->is_deleted) {
        return sqlite::utils::SetError(
            t, base::ErrStatus("dataframe already exists %s", name));
      }
      auto& df = v->ctx->tagged_dataframes.emplace_back();
      df.name = name;
      df.savepoint_version = v->savepoint_version;
      df.df_variant = *sqlite::value::Pointer<DataframeVariant>(
          argv[3], "DATAFRAME_VARIANT");
      return SQLITE_OK;
    }
    return sqlite::utils::SetError(t, "update is not supported");
  }

  // This needs to happen at the end as it depends on the functions
  // defined above.
  static constexpr sqlite3_module kModule = CreateModule();
};

}  // namespace perfetto::trace_processor

#endif  // SRC_TRACE_PROCESSOR_PERFETTO_SQL_ENGINE_DATAFRAME_STORAGE_MODULE_H_
