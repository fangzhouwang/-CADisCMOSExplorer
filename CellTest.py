#!/usr/bin/env python3


import unittest
from Cell import Cell
from ArkLibPy.ArkDBMySQL import ArkDBMySQL


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.db_ = ArkDBMySQL(db_config_file='/Users/Ark/.db_configs/db_config_local_cadis.txt')
        self.db_.set_table('WORK_LIB')

    def test_get_bsf_with_csim(self):
        str_netlist = "M0001 OUT01 VDD IN001 GND NMOS\n"
        test_cell = Cell(self.db_)
        test_cell.init_based_on_netlist(str_netlist)
        test_cell.cal_bsf()
        self.assertEqual(test_cell.bsf_, '01')

    def test_get_id(self):
        test_cell = Cell(self.db_)
        str_netlist = "M0001 OUT01 VDD IN001 GND NMOS\n"
        test_cell.init_based_on_netlist(str_netlist)
        test_cell.cal_bsf()
        self.assertEqual(1, test_cell.get_id())


if __name__ == '__main__':
    unittest.main()
