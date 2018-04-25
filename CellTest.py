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

    def test_get_family(self):
        cell = Cell(self.db_)
        cell.init_based_on_id(2)
        self.assertEqual('ULM', cell.get_family())

    def test_get_family_none(self):
        cell = Cell(self.db_)
        str_netlist = "M0001 IN005 VDD IN001 GND NMOS\n"
        cell.init_based_on_netlist(str_netlist)
        self.assertIsNone(cell.get_family())

    def test_clear_family(self):
        cell = Cell(self.db_)
        cell.init_based_on_id(1)
        cell.clear_family()
        self.assertIsNone(cell.get_family())

    def test_add_family(self):
        cell = Cell(self.db_)
        cell.init_based_on_id(1)

        cell.clear_family()
        cell.add_to_family('SingleTx')
        self.assertEqual('SingleTx', cell.get_family())

        # check adding same content twice, this should not affect the value
        cell.add_to_family('SingleTx')
        self.assertEqual('SingleTx', cell.get_family())
        cell.clear_family()


if __name__ == '__main__':
    unittest.main()
