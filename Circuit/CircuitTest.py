import unittest
from Circuit.Netlist import *


class NetlistTestCase(unittest.TestCase):
    def test_create_netlist(self):
        netlist = Netlist()
        str_netlist = "M0001 N0002 IN001 N0001 GND NMOS\n"\
                      "M0002 VDD N0001 N0002 GND NMOS\n" \
                      "M0003 N0001 IN001 IN002 VDD PMOS\n" \
                      "M0004 OUT01 N0001 IN002 VDD PMOS\n"
        netlist.set_netlist(str_netlist)
        self.assertEqual(str_netlist, str(netlist))

    def test_equ_netlist_swap_diff(self):
        netlist = Netlist()
        str_netlist = "M0001 VDD IN001 IN002 GND NMOS\n"
        netlist.set_netlist(str_netlist)
        equ_netlists = ["M0001 VDD IN001 IN002 GND NMOS\n",
                        "M0001 IN002 IN001 VDD GND NMOS\n",
                        "M0001 VDD IN002 IN001 GND NMOS\n",
                        "M0001 IN001 IN002 VDD GND NMOS\n"]
        self.assertCountEqual(equ_netlists, netlist.get_equ_netlists())

    def test_equ_netlist_complete_test_1(self):
        netlist = Netlist()
        str_netlist = "M0001 N0002 IN001 N0001 GND NMOS\n"
        netlist.set_netlist(str_netlist)
        equ_netlists = []
        with open('complete_test_results_1.txt') as results:
            temp_netlist = ''
            for line in results:
                if line == "\n":
                    equ_netlists.append(temp_netlist)
                    temp_netlist = ''
                    continue
                temp_netlist += line
        self.assertEqual(len(equ_netlists), len(list(netlist.get_equ_netlists())))
        self.assertCountEqual(equ_netlists, netlist.get_equ_netlists())

    def test_equ_netlist_complete_test_2(self):
        netlist = Netlist()
        str_netlist = "M0001 N0002 IN001 N0001 GND NMOS\n" \
                      "M0002 OUT01 N0001 IN002 VDD PMOS\n"
        netlist.set_netlist(str_netlist)
        equ_netlists = []
        with open('complete_test_results_2.txt') as results:
            temp_netlist = ''
            for line in results:
                if line == "\n":
                    equ_netlists.append(temp_netlist)
                    temp_netlist = ''
                    continue
                temp_netlist += line
        self.assertEqual(len(equ_netlists), len(list(netlist.get_equ_netlists())))
        self.assertCountEqual(equ_netlists, netlist.get_equ_netlists())

    def test_equ_netlist_complete_test_3(self):
        netlist = Netlist()
        str_netlist = "M0001 N0002 IN001 N0001 GND NMOS\n" \
                      "M0002 VDD N0001 N0002 GND NMOS\n" \
                      "M0003 N0001 IN001 IN002 VDD PMOS\n" \
                      "M0004 OUT01 N0001 IN002 VDD PMOS\n"
        netlist.set_netlist(str_netlist)
        equ_netlists = []
        with open('complete_test_results_3.txt') as results:
            temp_netlist = ''
            for line in results:
                if line == "\n":
                    equ_netlists.append(temp_netlist)
                    temp_netlist = ''
                    continue
                temp_netlist += line
        self.assertEqual(len(equ_netlists), len(list(netlist.get_equ_netlists())))
        self.assertCountEqual(equ_netlists, netlist.get_equ_netlists())


if __name__ == '__main__':
    unittest.main()
