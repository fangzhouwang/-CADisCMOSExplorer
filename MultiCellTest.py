import unittest

from Multi_cell import *


class MultiCellTestCase(unittest.TestCase):
    def test_multi_cell_INV_n_INV(self):
        str_netlist_1 = "M0001 GND IN001 OUT01 GND NMOS\n" \
                        "M0002 OUT01 IN001 VDD VDD PMOS\n"
        str_netlist_2 = "M0001 GND IN001 OUT01 GND NMOS\n" \
                        "M0002 OUT01 IN001 VDD VDD PMOS\n"

        multi_cell = MultiCell()
        iso, share = multi_cell.construct(str_netlist_1, str_netlist_2)
        self.assertCountEqual([], share)
        self.assertCountEqual([
           "M0001 GND IN001 N0001 GND NMOS\n"
           "M0002 GND N0001 OUT01 GND NMOS\n"
           "M0003 N0001 IN001 VDD VDD PMOS\n"
           "M0004 OUT01 N0001 VDD VDD PMOS\n"
        ], iso)

    def test_multi_cell_with_one_internal(self):
        str_netlist_1 = "M0001 GND IN001 OUT01 GND NMOS\n" \
                        "M0002 OUT01 IN001 VDD VDD PMOS\n"
        str_netlist_2 = "M0001 GND N0001 OUT01 GND NMOS\n" \
                        "M0002 OUT01 IN001 VDD VDD PMOS\n"

        multi_cell = MultiCell()
        iso, share = multi_cell.construct(str_netlist_1, str_netlist_2)
        self.assertCountEqual([], share)
        self.assertCountEqual([
            "M0001 GND IN001 N0002 GND NMOS\n"
            "M0002 GND N0001 OUT01 GND NMOS\n"
            "M0003 N0002 IN001 VDD VDD PMOS\n"
            "M0004 OUT01 N0002 VDD VDD PMOS\n"
        ], iso)

    def test_multi_cell_with_two_internal(self):
        str_netlist_1 = "M0001 GND IN001 N0001 GND NMOS\n" \
                        "M0002 OUT01 IN001 VDD VDD PMOS\n"
        str_netlist_2 = "M0001 GND N0001 OUT01 GND NMOS\n" \
                        "M0002 OUT01 IN001 VDD VDD PMOS\n"

        multi_cell = MultiCell()
        iso, share = multi_cell.construct(str_netlist_1, str_netlist_2)
        self.assertCountEqual([], share)
        self.assertCountEqual([
            "M0001 GND IN001 N0001 GND NMOS\n"
            "M0002 GND N0002 OUT01 GND NMOS\n"
            "M0003 N0003 IN001 VDD VDD PMOS\n"
            "M0004 OUT01 N0003 VDD VDD PMOS\n"
        ], iso)

    def test_multi_cell_with_two_inputs(self):
        str_netlist_1 = "M0001 GND IN001 N0001 GND NMOS\n" \
                        "M0002 OUT01 IN002 VDD VDD NMOS\n"
        str_netlist_2 = "M0001 IN001 IN002 IN003 GND NMOS\n"

        multi_cell = MultiCell()
        iso, share = multi_cell.construct(str_netlist_1, str_netlist_2)
        template_1 = "M0001 GND IN001 N0001 GND NMOS\n" \
                     "M0002 N0002 IN002 VDD GND NMOS\n"\
                     "M0003 IN003 N0002 IN004 GND NMOS\n"
        template_2 = "M0001 GND IN001 N0001 GND NMOS\n" \
                     "M0002 N0002 IN002 VDD GND NMOS\n" \
                     "M0003 N0002 IN003 IN004 GND NMOS\n"
        template_3 = "M0001 GND IN001 N0001 GND NMOS\n" \
                     "M0002 N0002 IN002 VDD GND NMOS\n" \
                     "M0003 IN003 IN004 N0002 GND NMOS\n"
        self.assertCountEqual([
            template_1.replace('IN004', 'IN003'),
            template_2.replace('IN004', 'IN003'),
            template_3.replace('IN004', 'IN003')
        ], iso)

        shared_golden = list()

        for replacements in product(('IN001', 'IN002', 'IN003'), repeat=2):
            if replacements[0] == replacements[1] and replacements[0] == 'IN003':
                continue
            shared_golden.append(template_1.replace('IN003', replacements[0]).replace('IN004', replacements[1]))
            shared_golden.append(template_2.replace('IN003', replacements[0]).replace('IN004', replacements[1]))
            shared_golden.append(template_3.replace('IN003', replacements[0]).replace('IN004', replacements[1]))
        self.assertCountEqual(shared_golden, share)

    def test_multi_cell_with_1_2(self):
        str_netlist_1 = "M0001 OUT01 VDD IN001 GND NMOS\n"
        str_netlist_2 = "M0001 VDD IN001 OUT01 GND NMOS\n"\
                        "M0002 OUT01 IN001 IN002 VDD PMOS\n"

        multi_cell = MultiCell()
        iso, share = multi_cell.construct(str_netlist_1, str_netlist_2)
        self.assertCountEqual([
            "M0001 N0001 VDD IN001 GND NMOS\nM0002 VDD N0001 OUT01 GND NMOS\nM0003 OUT01 N0001 IN001 VDD PMOS\n",
            "M0001 N0001 VDD IN001 GND NMOS\nM0002 VDD IN001 OUT01 GND NMOS\nM0003 OUT01 IN001 N0001 VDD PMOS\n"
        ], share)
        self.assertCountEqual([
            "M0001 N0001 VDD IN001 GND NMOS\nM0002 VDD N0001 OUT01 GND NMOS\nM0003 OUT01 N0001 IN002 VDD PMOS\n",
            "M0001 N0001 VDD IN001 GND NMOS\nM0002 VDD N0001 OUT01 GND NMOS\nM0003 OUT01 N0001 IN003 VDD PMOS\n",
            "M0001 N0001 VDD IN001 GND NMOS\nM0002 VDD IN002 OUT01 GND NMOS\nM0003 OUT01 IN002 N0001 VDD PMOS\n",
            "M0001 N0001 VDD IN001 GND NMOS\nM0002 VDD IN003 OUT01 GND NMOS\nM0003 OUT01 IN003 N0001 VDD PMOS\n"
        ], iso)


if __name__ == '__main__':
    unittest.main()
