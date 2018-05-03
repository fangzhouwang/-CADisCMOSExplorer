import unittest
from ArkLibPy.ArkDBMySQL import *

from Resistive_defect import ResistiveDefect


class ResistiveDefectTestCase(unittest.TestCase):
    def setUp(self):
        self.db_ = ArkDBMySQL(db_config_file='/Users/Ark/.db_configs/db_config_local_cadis.txt')
        self.db_.set_table("ONE_FIVE_LIB")

    def test_gen_defect_list(self):
        tester = ResistiveDefect(self.db_)
        tester.set_netlist(
            "M0001 GND N0001 OUT01 GND NMOS\n"
            "M0002 GND IN001 N0001 GND NMOS\n"
            "M0003 GND IN002 N0001 GND NMOS\n"
            "M0004 OUT01 IN001 IN002 VDD PMOS\n"
            "M0005 VDD IN002 N0001 VDD PMOS\n"
        )
        tester.gen_defect_list()
        self.assertCountEqual(
            [('GND', 'N0001'), ('GND', 'OUT01'), ('N0001', 'OUT01'), ('N0001', 'IN001'), ('N0001', 'IN002'),
             ('VDD', 'N0001'), ('OUT01', 'IN001'), ('OUT01', 'IN002'), ('VDD', 'OUT01')],
            tester.short_defects_
        )
        for i in range(len(tester.open_defects_)):
            defect_desc = tester.open_defects_[i]
            defect_desc[1] = sorted(defect_desc[1])

        self.assertCountEqual(
            [
                ['GND', ['M0001d']],
                ['GND', ['M0002d']],
                ['GND', ['M0003d']],
                ['N0001', ['M0001g']],
                ['N0001', ['M0002s', 'M0003s', 'M0005s']],
                ['N0001', ['M0002s']],
                ['N0001', ['M0001g', 'M0003s', 'M0005s']],
                ['N0001', ['M0003s']],
                ['N0001', ['M0001g', 'M0002s', 'M0005s']],
                ['N0001', ['M0005s']],
                ['N0001', ['M0001g', 'M0002s', 'M0003s']],
                ['N0001', ['M0001g', 'M0002s']],
                ['N0001', ['M0003s', 'M0005s']],
                ['N0001', ['M0001g', 'M0005s']],
                ['N0001', ['M0002s', 'M0003s']],
                ['N0001', ['M0001g', 'M0003s']],
                ['N0001', ['M0002s', 'M0005s']],
                ['OUT01', ['M0001s']],
                ['OUT01', ['M0004d']],
                ['IN001', ['M0002g']],
                ['IN001', ['M0004g']],
                ['IN002', ['M0003g']],
                ['IN002', ['M0004s']],
                ['IN002', ['M0005g']],
                ['VDD', ['M0005d']]
            ], tester.open_defects_
        )

    def test_gen_short_defect_str_netlists(self):
        tester = ResistiveDefect(self.db_)
        tester.set_netlist(
            "M0001 GND N0001 OUT01 GND NMOS\n"
            "M0002 GND IN001 N0001 GND NMOS\n"
            "M0003 GND IN002 N0001 GND NMOS\n"
            "M0004 OUT01 IN001 IN002 VDD PMOS\n"
            "M0005 VDD IN002 N0001 VDD PMOS\n"
        )
        tester.gen_defect_list()

        results = list()
        for short_defect in tester.short_defects_:
            results.append(tester.gen_short_defect_str_netlist(short_defect))

        self.assertCountEqual(
            [
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 GND VDD N0001 GND NMOS\n"
                "M1002 GND GND N0001 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 GND VDD OUT01 GND NMOS\n"
                "M1002 GND GND OUT01 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 N0001 VDD OUT01 GND NMOS\n"
                "M1002 N0001 GND OUT01 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 N0001 VDD IN001 GND NMOS\n"
                "M1002 N0001 GND IN001 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 N0001 VDD IN002 GND NMOS\n"
                "M1002 N0001 GND IN002 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 VDD VDD N0001 GND NMOS\n"
                "M1002 VDD GND N0001 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 OUT01 VDD IN001 GND NMOS\n"
                "M1002 OUT01 GND IN001 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 OUT01 VDD IN002 GND NMOS\n"
                "M1002 OUT01 GND IN002 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 VDD VDD OUT01 GND NMOS\n"
                "M1002 VDD GND OUT01 VDD PMOS\n"
            ], results
        )

    def test_gen_open_defect_str_netlists(self):
        tester = ResistiveDefect(self.db_)
        tester.set_netlist(
            "M0001 GND N0001 OUT01 GND NMOS\n"
            "M0002 GND IN001 N0001 GND NMOS\n"
            "M0003 GND IN002 N0001 GND NMOS\n"
            "M0004 OUT01 IN001 IN002 VDD PMOS\n"
            "M0005 VDD IN002 N0001 VDD PMOS\n"
        )
        tester.gen_defect_list()

        results = list()
        for open_defect in tester.open_defects_:
            results.append(tester.gen_open_defect_str_netlist(open_defect))

        self.assertCountEqual(
            [
                "M0001 N1000 N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 GND VDD N1000 GND NMOS\n"
                "M1002 GND GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 N1000 IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 GND VDD N1000 GND NMOS\n"
                "M1002 GND GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 N1000 IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 GND VDD N1000 GND NMOS\n"
                "M1002 GND GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N1000 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 N0001 VDD N1000 GND NMOS\n"
                "M1002 N0001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N1000 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 N0001 VDD N1000 GND NMOS\n"
                "M1002 N0001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N1000 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 N0001 VDD N1000 GND NMOS\n"
                "M1002 N0001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N1000 VDD PMOS\n"
                "M1001 N0001 VDD N1000 GND NMOS\n"
                "M1002 N0001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N1000 OUT01 GND NMOS\n"
                "M0002 GND IN001 N1000 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 N0001 VDD N1000 GND NMOS\n"
                "M1002 N0001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N1000 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N1000 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 N0001 VDD N1000 GND NMOS\n"
                "M1002 N0001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N1000 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N1000 VDD PMOS\n"
                "M1001 N0001 VDD N1000 GND NMOS\n"
                "M1002 N0001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N1000 GND NMOS\n"
                "M0003 GND IN002 N1000 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 N0001 VDD N1000 GND NMOS\n"
                "M1002 N0001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N1000 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N1000 VDD PMOS\n"
                "M1001 N0001 VDD N1000 GND NMOS\n"
                "M1002 N0001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N1000 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N1000 VDD PMOS\n"
                "M1001 N0001 VDD N1000 GND NMOS\n"
                "M1002 N0001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N1000 OUT01 GND NMOS\n"
                "M0002 GND IN001 N1000 GND NMOS\n"
                "M0003 GND IN002 N1000 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 N0001 VDD N1000 GND NMOS\n"
                "M1002 N0001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N1000 OUT01 GND NMOS\n"
                "M0002 GND IN001 N1000 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N1000 VDD PMOS\n"
                "M1001 N0001 VDD N1000 GND NMOS\n"
                "M1002 N0001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N1000 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N1000 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N1000 VDD PMOS\n"
                "M1001 N0001 VDD N1000 GND NMOS\n"
                "M1002 N0001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N1000 GND NMOS\n"
                "M0003 GND IN002 N1000 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N1000 VDD PMOS\n"
                "M1001 N0001 VDD N1000 GND NMOS\n"
                "M1002 N0001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 N1000 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 OUT01 VDD N1000 GND NMOS\n"
                "M1002 OUT01 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 N1000 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 OUT01 VDD N1000 GND NMOS\n"
                "M1002 OUT01 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND N1000 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 IN001 VDD N1000 GND NMOS\n"
                "M1002 IN001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 N1000 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 IN001 VDD N1000 GND NMOS\n"
                "M1002 IN001 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND N1000 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 IN002 VDD N1000 GND NMOS\n"
                "M1002 IN002 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 N1000 VDD PMOS\n"
                "M0005 VDD IN002 N0001 VDD PMOS\n"
                "M1001 IN002 VDD N1000 GND NMOS\n"
                "M1002 IN002 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 VDD N1000 N0001 VDD PMOS\n"
                "M1001 IN002 VDD N1000 GND NMOS\n"
                "M1002 IN002 GND N1000 VDD PMOS\n"
                ,
                "M0001 GND N0001 OUT01 GND NMOS\n"
                "M0002 GND IN001 N0001 GND NMOS\n"
                "M0003 GND IN002 N0001 GND NMOS\n"
                "M0004 OUT01 IN001 IN002 VDD PMOS\n"
                "M0005 N1000 IN002 N0001 VDD PMOS\n"
                "M1001 VDD VDD N1000 GND NMOS\n"
                "M1002 VDD GND N1000 VDD PMOS\n"
            ], results
        )

    def test_get_defect_info_dict(self):
        tester = ResistiveDefect(self.db_)
        str_netlist = "M0001 OUT01 VDD IN001 GND NMOS\n"
        tester.set_netlist(str_netlist)
        defect = ('OUT01', 'VDD')
        defect_type = 'short'
        self.assertEqual(
            {'FAULT_TYPE': 'short', 'FAULT_DESC': "('OUT01', 'VDD')",
             'FAULTY_NETLIST': "M0001 OUT01 VDD IN001 GND NMOS\n"
                               "M1001 OUT01 VDD VDD GND NMOS\n"
                               "M1002 OUT01 GND VDD VDD PMOS\n",
             'FAULTY_BSF': 'R1', 'FAULTY_BSF_weak': 'R1', 'FAULTY_VEC_CNT': 1, 'FAULTY_VEC_CNT_weak': 2}
            , tester.get_defect_info_dict(defect, defect_type)
        )

    def test_get_all_defect_info_dicts(self):
        tester = ResistiveDefect(self.db_)
        str_netlist = "M0001 OUT01 VDD IN001 GND NMOS\n"
        tester.set_netlist(str_netlist)
        self.assertEqual(
            [{'FAULT_TYPE': 'open', 'FAULT_DESC': "['VDD', ['M0001g']]",
              'FAULTY_NETLIST': "M0001 OUT01 N1000 IN001 GND NMOS\n"
                                "M1001 VDD VDD N1000 GND NMOS\n"
                                "M1002 VDD GND N1000 VDD PMOS\n",
              'FAULTY_BSF': '01', 'FAULTY_BSF_weak': '0i', 'FAULTY_VEC_CNT': 0, 'FAULTY_VEC_CNT_weak': 0},
             {'FAULT_TYPE': 'open', 'FAULT_DESC': "['IN001', ['M0001s']]",
              'FAULTY_NETLIST': "M0001 OUT01 VDD N1000 GND NMOS\n"
                                "M1001 IN001 VDD N1000 GND NMOS\n"
                                "M1002 IN001 GND N1000 VDD PMOS\n",
              'FAULTY_BSF': '01', 'FAULTY_BSF_weak': '0i', 'FAULTY_VEC_CNT': 0, 'FAULTY_VEC_CNT_weak': 0},
             {'FAULT_TYPE': 'short', 'FAULT_DESC': "('VDD', 'OUT01')",
              'FAULTY_NETLIST': "M0001 OUT01 VDD IN001 GND NMOS\n"
                                "M1001 VDD VDD OUT01 GND NMOS\n"
                                "M1002 VDD GND OUT01 VDD PMOS\n",
              'FAULTY_BSF': 'R1', 'FAULTY_BSF_weak': 'R1', 'FAULTY_VEC_CNT': 1, 'FAULTY_VEC_CNT_weak': 2},
             {'FAULT_TYPE': 'short', 'FAULT_DESC': "('OUT01', 'IN001')",
              'FAULTY_NETLIST': "M0001 OUT01 VDD IN001 GND NMOS\n"
                                "M1001 OUT01 VDD IN001 GND NMOS\n"
                                "M1002 OUT01 GND IN001 VDD PMOS\n",
              'FAULTY_BSF': '01', 'FAULTY_BSF_weak': '01', 'FAULTY_VEC_CNT': 0, 'FAULTY_VEC_CNT_weak': 1}]
            , tester.get_all_defect_info_dicts()
        )

    def test_insert_defect_details_for_id_cell(self):
        tester = ResistiveDefect(self.db_)
        tester.insert_defect_details_for_id_cell(1)


if __name__ == '__main__':
    unittest.main()
