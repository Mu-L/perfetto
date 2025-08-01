#!/usr/bin/env python3
# Copyright (C) 2024 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License a
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from python.generators.diff_tests.testing import Csv, Path, DataPath
from python.generators.diff_tests.testing import DiffTestBlueprint
from python.generators.diff_tests.testing import TestSuite


class WattsonStdlib(TestSuite):
  # Test that the device name can be extracted from the trace's metadata.
  def test_wattson_device_name(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_wo_device_name.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.device_infos;
            select name from _wattson_device
            """),
        out=Csv("""
            "name"
            "monaco"
            """))

  # Tests intermediate table
  def test_wattson_intermediate_table(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.estimates;
              select
                ts,dur,l3_hit_count,l3_miss_count,freq_0,idle_0,freq_1,idle_1,freq_2,idle_2,freq_3,idle_3,freq_4,idle_4,freq_5,idle_5,freq_6,idle_6,freq_7,idle_7,no_static,cpu4_curve,cpu5_curve,cpu6_curve,cpu7_curve
              from _w_independent_cpus_calc
              WHERE ts > 359661672577
              ORDER by ts ASC
              LIMIT 10
            """),
        out=Csv("""
          "ts","dur","l3_hit_count","l3_miss_count","freq_0","idle_0","freq_1","idle_1","freq_2","idle_2","freq_3","idle_3","freq_4","idle_4","freq_5","idle_5","freq_6","idle_6","freq_7","idle_7","no_static","cpu4_curve","cpu5_curve","cpu6_curve","cpu7_curve"
          359661672578,75521,8326,9689,1401000,0,1401000,0,1401000,0,1401000,0,2253000,-1,2253000,0,2802000,-1,2802000,0,0,527.050000,23.500000,1942.890000,121.430000
          359661748099,2254517,248577,289258,1401000,0,1401000,0,1401000,0,1401000,0,2253000,0,2253000,0,2802000,-1,2802000,0,0,23.500000,23.500000,1942.890000,121.430000
          359664003674,11596,1278,1487,1401000,-1,1401000,-1,1401000,-1,1401000,-1,2253000,-1,2253000,-1,2802000,-1,2802000,-1,-1,527.050000,527.050000,1942.890000,1942.890000
          359664015270,4720,520,605,1401000,-1,1401000,-1,1401000,-1,1401000,-1,2253000,-1,2253000,-1,2802000,-1,2802000,0,-1,527.050000,527.050000,1942.890000,121.430000
          359664019990,18921,2086,2427,1401000,-1,1401000,-1,1401000,-1,1401000,-1,2253000,0,2253000,-1,2802000,-1,2802000,0,-1,23.500000,527.050000,1942.890000,121.430000
          359664038911,8871,978,1138,1401000,-1,1401000,-1,1401000,0,1401000,-1,2253000,0,2253000,-1,2802000,-1,2802000,0,-1,23.500000,527.050000,1942.890000,121.430000
          359664047782,1343,148,172,1401000,-1,1401000,0,1401000,0,1401000,-1,2253000,0,2253000,-1,2802000,-1,2802000,0,-1,23.500000,527.050000,1942.890000,121.430000
          359664049491,1383,152,177,1401000,0,1401000,0,1401000,0,1401000,-1,2253000,0,2253000,0,2802000,-1,2802000,0,-1,23.500000,23.500000,1942.890000,121.430000
          359664050874,2409912,265711,309195,1401000,0,1401000,0,1401000,0,1401000,0,2253000,0,2253000,0,2802000,-1,2802000,0,0,23.500000,23.500000,1942.890000,121.430000
          359666460786,13754,1516,1764,1401000,0,1401000,0,1401000,0,1401000,0,2253000,-1,2253000,0,2802000,-1,2802000,0,0,527.050000,23.500000,1942.890000,121.430000
            """))

  # Tests that device static curve selection is only when CPUs are active
  def test_wattson_static_curve_selection(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.estimates;
              SELECT
                ts,dur,cpu0_curve,cpu1_curve,cpu2_curve,cpu3_curve,cpu4_curve,cpu5_curve,cpu6_curve,cpu7_curve,static_curve,l3_hit_value,l3_miss_value
              FROM _system_state_curves
              ORDER by ts ASC
              LIMIT 5
            """),
        out=Csv("""
            "ts","dur","cpu0_curve","cpu1_curve","cpu2_curve","cpu3_curve","cpu4_curve","cpu5_curve","cpu6_curve","cpu7_curve","static_curve","l3_hit_value","l3_miss_value"
            359085636893,23030,0.000000,"[NULL]",0.000000,0.000000,0.000000,28.510000,0.000000,0.000000,0.000000,"[NULL]","[NULL]"
            359085659923,6664673,0.000000,"[NULL]",0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000
            359092324596,1399699,0.000000,"[NULL]",0.000000,21.840000,0.000000,0.000000,0.000000,0.000000,3.730000,"[NULL]","[NULL]"
            359093724295,6959391,0.000000,"[NULL]",0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000
            359100683686,375122,0.000000,"[NULL]",0.000000,0.000000,28.510000,0.000000,0.000000,0.000000,0.000000,"[NULL]","[NULL]"
            """))

  # Tests that L3 cache calculations are being done correctly
  def test_wattson_l3_calculations(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.estimates;
              SELECT
                ts,dur,cpu0_curve,cpu1_curve,cpu2_curve,cpu3_curve,cpu4_curve,cpu5_curve,cpu6_curve,cpu7_curve,static_curve,l3_hit_value,l3_miss_value
              FROM _system_state_curves
              WHERE ts > 359661672577
              ORDER by ts ASC
              LIMIT 5
            """),
        out=Csv("""
            "ts","dur","cpu0_curve","cpu1_curve","cpu2_curve","cpu3_curve","cpu4_curve","cpu5_curve","cpu6_curve","cpu7_curve","static_curve","l3_hit_value","l3_miss_value"
            359661672578,75521,3.450000,3.450000,3.450000,3.450000,527.050000,23.500000,1942.890000,121.430000,35.640000,19381.262800,8783.078500
            359661748099,2254517,3.450000,3.450000,3.450000,3.450000,23.500000,23.500000,1942.890000,121.430000,35.640000,578637.540600,262212.377000
            359664003674,11596,208.140000,208.140000,208.140000,208.140000,527.050000,527.050000,1942.890000,1942.890000,35.640000,2974.928400,1347.965500
            359664015270,4720,208.140000,208.140000,208.140000,208.140000,527.050000,527.050000,1942.890000,121.430000,35.640000,1210.456000,548.432500
            359664019990,18921,208.140000,208.140000,208.140000,208.140000,23.500000,527.050000,1942.890000,121.430000,35.640000,4855.790800,2200.075500
            """))

  # Tests calculations when everything in system state is converted to mW
  def test_wattson_system_state_mw_calculations(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.estimates;
              SELECT
                ts, dur, cpu0_mw, cpu1_mw, cpu2_mw, cpu3_mw, cpu4_mw, cpu5_mw,
                cpu6_mw, cpu7_mw, dsu_scu_mw
              FROM _system_state_mw
              WHERE ts > 359661672577
              ORDER by ts ASC
              LIMIT 10
            """),
        out=Csv("""
            "ts","dur","cpu0_mw","cpu1_mw","cpu2_mw","cpu3_mw","cpu4_mw","cpu5_mw","cpu6_mw","cpu7_mw","dsu_scu_mw"
            359661672578,75521,3.450000,3.450000,3.450000,3.450000,527.050000,23.500000,1942.890000,121.430000,408.573903
            359661748099,2254517,3.450000,3.450000,3.450000,3.450000,23.500000,23.500000,1942.890000,121.430000,408.602332
            359664003674,11596,208.140000,208.140000,208.140000,208.140000,527.050000,527.050000,1942.890000,1942.890000,408.431816
            359664015270,4720,208.140000,208.140000,208.140000,208.140000,527.050000,527.050000,1942.890000,121.430000,408.285869
            359664019990,18921,208.140000,208.140000,208.140000,208.140000,23.500000,527.050000,1942.890000,121.430000,408.551913
            359664038911,8871,208.140000,208.140000,3.450000,208.140000,23.500000,527.050000,1942.890000,121.430000,408.561362
            359664047782,1343,208.140000,3.450000,3.450000,208.140000,23.500000,527.050000,1942.890000,121.430000,408.262785
            359664049491,1383,3.450000,3.450000,3.450000,208.140000,23.500000,23.500000,1942.890000,121.430000,407.495459
            359664050874,2409912,3.450000,3.450000,3.450000,3.450000,23.500000,23.500000,1942.890000,121.430000,408.602720
            359666460786,13754,3.450000,3.450000,3.450000,3.450000,527.050000,23.500000,1942.890000,121.430000,408.477778
            """))

  # Tests that suspend values are being skipped
  def test_wattson_suspend_calculations(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_eos_suspend.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.estimates;
              SELECT
                ts,dur,cpu0_curve,cpu1_curve,cpu2_curve,cpu3_curve,cpu4_curve,cpu5_curve,cpu6_curve,cpu7_curve,static_curve,l3_hit_value,l3_miss_value
              FROM _system_state_curves
              WHERE ts > 24790009884888
              ORDER by ts ASC
              LIMIT 5
            """),
        out=Csv("""
            "ts","dur","cpu0_curve","cpu1_curve","cpu2_curve","cpu3_curve","cpu4_curve","cpu5_curve","cpu6_curve","cpu7_curve","static_curve","l3_hit_value","l3_miss_value"
            24790009907857,2784616769,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0,0
            24792794524626,424063,39.690000,39.690000,39.690000,39.690000,0.000000,0.000000,0.000000,0.000000,18.390000,"[NULL]","[NULL]"
            24792794948689,205625,39.690000,39.690000,39.690000,39.690000,0.000000,0.000000,0.000000,0.000000,18.390000,"[NULL]","[NULL]"
            24792795154314,19531,39.690000,39.690000,39.690000,39.690000,0.000000,0.000000,0.000000,0.000000,18.390000,"[NULL]","[NULL]"
            24792795173845,50781,39.690000,39.690000,0.000000,39.690000,0.000000,0.000000,0.000000,0.000000,18.390000,"[NULL]","[NULL]"
            """))

  # Tests that total calculations are correct
  def test_wattson_idle_attribution(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_eos_suspend.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.tasks.idle_transitions_attribution;
            SELECT
              SUM(estimated_mw * dur) / 1000000000 as idle_transition_cost_mws,
              utid,
              upid
            FROM _idle_transition_cost
            GROUP BY utid
            ORDER BY idle_transition_cost_mws DESC
            LIMIT 20
            """),
        out=Csv("""
            "idle_transition_cost_mws","utid","upid"
            19.068358,10,10
            7.642105,73,73
            6.069991,146,146
            4.887564,457,457
            4.641823,694,353
            4.575867,1262,401
            4.513442,515,137
            3.819375,169,169
            3.803823,11,11
            3.617314,147,147
            3.522582,396,396
            3.385840,486,486
            3.351066,727,356
            3.279231,606,326
            3.155939,464,464
            2.949362,29,29
            2.848033,414,414
            2.660892,471,471
            2.573006,1270,401
            2.488196,172,172
            """))

  # Tests that DSU devfreq calculations are merged correctly
  def test_wattson_dsu_devfreq(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_tk4_pcmark.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.cpu.w_dsu_dependence;
            SELECT
            ts,dur,freq_0,idle_0,freq_1,idle_1,freq_2,idle_2,freq_3,idle_3,cpu4_curve,cpu5_curve,cpu6_curve,cpu7_curve,l3_hit_count,l3_miss_count,no_static,all_cpu_deep_idle
            FROM _cpu_curves
            WHERE ts > 4108586775197
            LIMIT 20
            """),
        out=Csv("""
            "ts","dur","freq_0","idle_0","freq_1","idle_1","freq_2","idle_2","freq_3","idle_3","cpu4_curve","cpu5_curve","cpu6_curve","cpu7_curve","l3_hit_count","l3_miss_count","no_static","all_cpu_deep_idle"
            4108586789603,35685,1950000,0,1950000,-1,1950000,-1,1950000,-1,674.240000,674.240000,674.240000,3327.560000,14718,5837,-1,-1
            4108586825288,30843,1950000,-1,1950000,-1,1950000,-1,1950000,-1,674.240000,674.240000,674.240000,3327.560000,12721,5045,-1,-1
            4108586856131,13387,1950000,-1,1950000,-1,1950000,-1,1950000,-1,674.240000,674.240000,674.240000,99.470000,5521,2189,-1,-1
            4108586869518,22542,1950000,-1,1950000,-1,1950000,-1,1950000,-1,674.240000,674.240000,674.240000,3327.560000,9297,3687,-1,-1
            4108586892060,2482,1950000,-1,1950000,-1,1950000,-1,1950000,0,674.240000,674.240000,674.240000,3327.560000,1023,406,-1,-1
            4108586894542,68563,1950000,-1,1950000,-1,1950000,-1,1950000,-1,674.240000,674.240000,674.240000,3327.560000,28279,11216,-1,-1
            4108586963105,59652,1950000,-1,1950000,-1,1950000,-1,1950000,0,674.240000,674.240000,674.240000,3327.560000,24603,9758,-1,-1
            4108587022757,3743,1950000,0,1950000,-1,1950000,-1,1950000,0,674.240000,674.240000,674.240000,3327.560000,1543,612,-1,-1
            4108587026500,15992,1950000,-1,1950000,-1,1950000,-1,1950000,0,674.240000,674.240000,674.240000,3327.560000,6595,2616,-1,-1
            4108587042492,15625,1950000,-1,1950000,-1,1950000,-1,1950000,0,674.240000,674.240000,674.240000,99.470000,6444,2556,-1,-1
            4108587058117,8138,1950000,-1,1950000,-1,1950000,-1,1950000,0,674.240000,674.240000,674.240000,3327.560000,3356,1331,-1,-1
            4108587066255,80566,1950000,-1,1950000,-1,1950000,-1,1950000,-1,674.240000,674.240000,674.240000,3327.560000,33229,13179,-1,-1
            4108587146821,19572,1950000,-1,1950000,-1,1950000,-1,1950000,-1,674.240000,674.240000,674.240000,99.470000,8072,3201,-1,-1
            4108587166393,219116,1950000,-1,1950000,-1,1950000,-1,1950000,-1,674.240000,674.240000,674.240000,3327.560000,90375,35845,-1,-1
            4108587385509,81991,1950000,-1,1950000,0,1950000,-1,1950000,-1,674.240000,674.240000,674.240000,3327.560000,33817,13413,-1,-1
            4108587467500,90413,1950000,-1,1950000,0,1950000,0,1950000,-1,674.240000,674.240000,674.240000,3327.560000,37291,14790,-1,-1
            4108587557913,92896,1950000,0,1950000,0,1950000,0,1950000,-1,674.240000,674.240000,674.240000,3327.560000,38315,15196,-1,-1
            4108587650809,95296,1950000,-1,1950000,0,1950000,0,1950000,-1,674.240000,674.240000,674.240000,3327.560000,39305,15589,-1,-1
            4108587746105,12451,1950000,0,1950000,0,1950000,0,1950000,-1,674.240000,674.240000,674.240000,3327.560000,5135,2036,-1,-1
            4108587758556,28524,1950000,0,1950000,0,1950000,-1,1950000,-1,674.240000,674.240000,674.240000,3327.560000,11764,4666,-1,-1
            """))

  # Tests that DSU devfreq calculations are merged correctly
  def test_wattson_dsu_devfreq_system_state(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_tk4_pcmark.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.estimates;
            SELECT
               ts, dur, cpu0_mw, cpu1_mw, cpu2_mw, cpu3_mw, cpu4_mw, cpu5_mw,
               cpu6_mw, cpu7_mw, dsu_scu_mw
            FROM _system_state_mw
            WHERE ts > 4108586775197
            LIMIT 20
            """),
        out=Csv("""
            "ts","dur","cpu0_mw","cpu1_mw","cpu2_mw","cpu3_mw","cpu4_mw","cpu5_mw","cpu6_mw","cpu7_mw","dsu_scu_mw"
            4108586789603,35685,2.670000,205.600000,205.600000,205.600000,674.240000,674.240000,674.240000,3327.560000,1166.695271
            4108586825288,30843,205.600000,205.600000,205.600000,205.600000,674.240000,674.240000,674.240000,3327.560000,1166.698554
            4108586856131,13387,205.600000,205.600000,205.600000,205.600000,674.240000,674.240000,674.240000,99.470000,1166.545753
            4108586869518,22542,205.600000,205.600000,205.600000,205.600000,674.240000,674.240000,674.240000,3327.560000,1166.655587
            4108586892060,2482,205.600000,205.600000,205.600000,2.670000,674.240000,674.240000,674.240000,3327.560000,1166.164641
            4108586894542,68563,205.600000,205.600000,205.600000,205.600000,674.240000,674.240000,674.240000,3327.560000,1166.746124
            4108586963105,59652,205.600000,205.600000,205.600000,2.670000,674.240000,674.240000,674.240000,3327.560000,1166.716706
            4108587022757,3743,2.670000,205.600000,205.600000,2.670000,674.240000,674.240000,674.240000,3327.560000,1166.170321
            4108587026500,15992,205.600000,205.600000,205.600000,2.670000,674.240000,674.240000,674.240000,3327.560000,1166.620056
            4108587042492,15625,205.600000,205.600000,205.600000,2.670000,674.240000,674.240000,674.240000,99.470000,1166.668234
            4108587058117,8138,205.600000,205.600000,205.600000,2.670000,674.240000,674.240000,674.240000,3327.560000,1166.555033
            4108587066255,80566,205.600000,205.600000,205.600000,205.600000,674.240000,674.240000,674.240000,3327.560000,1166.717766
            4108587146821,19572,205.600000,205.600000,205.600000,205.600000,674.240000,674.240000,674.240000,99.470000,1166.626795
            4108587166393,219116,205.600000,205.600000,205.600000,205.600000,674.240000,674.240000,674.240000,3327.560000,1166.750356
            4108587385509,81991,205.600000,2.670000,205.600000,205.600000,674.240000,674.240000,674.240000,3327.560000,1166.743880
            4108587467500,90413,205.600000,2.670000,2.670000,205.600000,674.240000,674.240000,674.240000,3327.560000,1166.736713
            4108587557913,92896,2.670000,2.670000,2.670000,205.600000,674.240000,674.240000,674.240000,3327.560000,1166.730805
            4108587650809,95296,205.600000,2.670000,2.670000,205.600000,674.240000,674.240000,674.240000,3327.560000,1166.740927
            4108587746105,12451,2.670000,2.670000,2.670000,205.600000,674.240000,674.240000,674.240000,3327.560000,1166.556475
            4108587758556,28524,2.670000,2.670000,205.600000,205.600000,674.240000,674.240000,674.240000,3327.560000,1166.680924
            """))

  def test_wattson_time_window_api(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query="""
        INCLUDE PERFETTO MODULE wattson.estimates;

        SELECT
          cpu0_mw,
          cpu1_mw,
          cpu2_mw,
          cpu3_mw,
          cpu4_mw,
          cpu5_mw,
          cpu6_mw,
          cpu7_mw,
          dsu_scu_mw
        FROM _windowed_system_state_mw(362426061658, 5067704349)
        """,
        out=Csv("""
            "cpu0_mw","cpu1_mw","cpu2_mw","cpu3_mw","cpu4_mw","cpu5_mw","cpu6_mw","cpu7_mw","dsu_scu_mw"
            13.118584,6.316953,5.480104,8.866060,8.937174,10.717942,29.482823,30.239208,25.756299
            """))

  # Tests that suspend calculations are correct on 8 CPU device where suspend
  # indication comes from "syscore" command
  def test_wattson_syscore_suspend(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_syscore_suspend.pb'),
        query=("""
            INCLUDE PERFETTO MODULE intervals.intersect;
            INCLUDE PERFETTO MODULE wattson.estimates;

            SELECT
              ii.ts,
              ii.dur,
              stats.cpu0_id,
              stats.cpu1_id,
              stats.cpu2_id,
              stats.cpu3_id,
              ss.power_state = 'suspended' AS suspended
            FROM _interval_intersect!(
              (
                _ii_subquery!(_stats_cpu0123),
                _ii_subquery!(android_suspend_state)
              ),
              ()
            ) AS ii
            JOIN _stats_cpu0123 AS stats
              ON stats._auto_id = id_0
            JOIN android_suspend_state AS ss
              ON ss._auto_id = id_1
            WHERE suspended
            """),
        out=Csv("""
            "ts","dur","cpu0_id","cpu1_id","cpu2_id","cpu3_id","suspended"
            385019771468,61975407053,12042,12219,10489,8911,1
            448320364476,3674872885,13008,12957,11169,9275,1
            452415394221,69579176303,13659,13366,11656,9614,1
            564873995228,135118729231,45230,37601,22805,20139,1
            """))

  # Tests traces from VM that have incomplete CPU tracks
  def test_wattson_missing_cpus_on_guest(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_tk4_vm.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.estimates;
               SELECT
                 ts, dur, cpu0_mw, cpu1_mw, cpu2_mw, cpu3_mw, cpu4_mw, cpu5_mw,
                 cpu6_mw
               FROM _system_state_mw
               WHERE ts > 25150000000
               LIMIT 10
            """),
        out=Csv("""
            "ts","dur","cpu0_mw","cpu1_mw","cpu2_mw","cpu3_mw","cpu4_mw","cpu5_mw","cpu6_mw"
            25150029000,1080,0.000000,0.000000,0.000000,0.000000,70.050000,83.260000,0.000000
            25150030640,42920,0.000000,0.000000,0.000000,0.000000,70.050000,70.050000,0.000000
            25150073560,99800,0.000000,0.000000,0.000000,0.000000,70.050000,0.000000,0.000000
            25150173360,28240,176.280000,0.000000,0.000000,0.000000,70.050000,0.000000,0.000000
            25150201600,6480,176.280000,0.000000,0.000000,176.280000,70.050000,0.000000,0.000000
            25150208080,29840,176.280000,0.000000,0.000000,176.280000,70.050000,70.050000,0.000000
            25150237920,129800,0.000000,0.000000,0.000000,176.280000,70.050000,70.050000,0.000000
            25150367720,37480,0.000000,0.000000,0.000000,176.280000,70.050000,0.000000,0.000000
            25150405200,15120,0.000000,176.280000,0.000000,176.280000,70.050000,0.000000,0.000000
            25150420320,15920,0.000000,176.280000,0.000000,0.000000,70.050000,0.000000,0.000000
            """))

  # Tests suspend path with devfreq code path
  def test_wattson_devfreq_hotplug_and_suspend(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_cpuhp_devfreq_suspend.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.estimates;
               SELECT
                 ts, dur, cpu0_mw, cpu1_mw, cpu2_mw, cpu3_mw, cpu4_mw, cpu5_mw,
                 cpu6_mw, cpu7_mw, dsu_scu_mw
               FROM _system_state_mw
               WHERE ts > 165725449108
              LIMIT 6
            """),
        out=Csv("""
            "ts","dur","cpu0_mw","cpu1_mw","cpu2_mw","cpu3_mw","cpu4_mw","cpu5_mw","cpu6_mw","cpu7_mw","dsu_scu_mw"
            165725450194,7527,111.020000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,375.490000,14.560000
            165725457721,17334,111.020000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,14.560000
            165725475055,6999,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000
            165725482054,1546,111.020000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,14.560000
            165725483600,4468465,111.020000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,14.560000
            165729952065,73480460119,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000
            """))

  # Tests remapping of idle states
  def test_wattson_idle_remap(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_idle_map.pb'),
        query=("""
               INCLUDE PERFETTO MODULE wattson.estimates;
               SELECT ts, dur, cpu, idle
               FROM _adjusted_deep_idle
               WHERE ts > 1450338950433 AND cpu = 3
               LIMIT 10
               """),
        out=Csv("""
               "ts","dur","cpu","idle"
               1450338950434,1395365,3,1
               1450340345799,96927,3,-1
               1450340442726,301250,3,0
               1450340743976,24010,3,-1
               1450340767986,3748386,3,1
               1450344516372,70208,3,-1
               1450344586580,2400521,3,1
               1450346987101,306458,3,-1
               1450347293559,715573,3,0
               1450348009132,82292,3,-1
               """))

  # Tests that hotplug slices that defined CPU off region are correct
  def test_wattson_hotplug_tk(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_cpuhp_devfreq_suspend.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.cpu.hotplug;
            SELECT cpu, ts, dur
            FROM _gapless_hotplug_slices
            WHERE cpu < 2
            """),
        out=Csv("""
            "cpu","ts","dur"
            0,86747008512,302795933205
            1,86747008512,3769632400
            1,90516640912,4341919
            1,90520982831,73692291133
            1,164213273964,1478796428
            1,165692070392,73525895666
            1,239217966058,10896074956
            1,250114041014,95948
            1,250114136962,4705159
            1,250118842121,137102890041
            1,387221732162,2321209555
            """))

  # Tests that IRQ stacks are properly flattened and have unique IDs
  def test_wattson_irq_flattening(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_irq_gpu_markers.pb'),
        query="""
        INCLUDE PERFETTO MODULE wattson.tasks.task_slices;

        SELECT
          SUM(dur) AS total_dur, irq_name, irq_id
        FROM  _all_irqs_flattened_slices
        GROUP BY irq_name
        LIMIT 10
        """,
        out=Csv("""
          "total_dur","irq_name","irq_id"
          1118451,"BLOCK",-7563548160659491326
          1701414,"IRQ (100a0000.BIG)",-8960469306195608742
          769330,"IRQ (100a0000.LITTLE)",2595235052520049942
          741289,"IRQ (100a0000.MID)",709594339438163430
          2179935,"IRQ (10840000.pinctrl)",6369664009351169759
          1192993,"IRQ (10970000.hsi2c)",-1238860297262945668
          7840694,"IRQ (176a0000.mbox)",442503679933451729
          2110993,"IRQ (1c0b0000.drmdpp)",3108582083943637163
          2132254,"IRQ (1c0b1000.drmdpp)",2330704911466106250
          1187454,"IRQ (1c0b2000.drmdpp)",-4397375750993244671
          """))

  # Tests that all tasks are correct after accounting for preemption and idle
  # exits
  def test_wattson_all_tasks_flattening_and_idle_exits(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_irq_gpu_markers.pb'),
        query="""
        INCLUDE PERFETTO MODULE wattson.tasks.task_slices;

        SELECT
          SUM(dur) AS dur,
          thread_name
        FROM _wattson_task_slices
        GROUP BY thread_name
        ORDER BY dur DESC
        LIMIT 10
        """,
        out=Csv("""
          "dur","thread_name"
          80559339989,"swapper"
          1617087785,"Runner: gl_tess"
          800487950,"mali-cmar-backe"
          469271586,"mali_jd_thread"
          426019439,"surfaceflinger"
          326858956,"IRQ (exynos-mct)"
          323531361,"s.nexuslauncher"
          312153973,"RenderThread"
          251889143,"50000.corporate"
          241043219,"traced_probes"
          """))
