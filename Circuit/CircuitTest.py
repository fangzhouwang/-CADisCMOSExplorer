import unittest
from Circuit.Netlist import *
from Circuit.CSim import *


class CSimTestCase(unittest.TestCase):
    def test_csim(self):
        str_netlist = "M0001 GND IN001 OUT01 GND NMOS\n" \
                      "M0002 VDD IN001 OUT01 VDD PMOS\n"
        bsf, bsf_weak = csim(str_netlist)
        self.assertEqual(bsf, '10')
        self.assertEqual(bsf_weak, '10')


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

    def test_update_transistors(self):
        netlist = Netlist()
        str_netlist = "M0003 N0002 IN001 N0001 GND NMOS\n" \
                      "M0008 VDD N0001 N0002 GND NMOS\n" \
                      "M0001 N0001 IN001 IN002 VDD PMOS\n" \
                      "M0003 OUT01 N0001 IN002 VDD PMOS\n"
        netlist.set_netlist(str_netlist)
        netlist.update_transistor_names()
        cnt = 1
        for transistor in netlist.get_transistors():
            self.assertEqual(int(transistor.get_name()[1:]), cnt)
            cnt += 1

    def test_remove_transistor(self):
        netlist = Netlist()
        str_netlist = "M0003 N0002 IN001 N0001 GND NMOS\n" \
                      "M0008 VDD N0001 N0002 GND NMOS\n" \
                      "M0001 N0001 IN001 IN002 VDD PMOS\n" \
                      "M0003 OUT01 N0001 IN002 VDD PMOS\n"
        netlist.set_netlist(str_netlist)
        netlist.remove_transistor("M0008", True)
        str_netlist = "M0001 N0002 IN001 N0001 GND NMOS\n" \
                      "M0002 N0001 IN001 IN002 VDD PMOS\n" \
                      "M0003 OUT01 N0001 IN002 VDD PMOS\n"
        self.assertEqual(str_netlist, netlist.get_netlist_string())
        self.assertEqual(len(netlist.p_transistors_), 2)
        self.assertEqual(len(netlist.n_transistors_), 1)

    def test_remove_transistor_with_dup(self):
        netlist = Netlist()
        str_netlist = "M0003 N0002 IN001 N0001 GND NMOS\n" \
                      "M0008 VDD N0001 N0002 GND NMOS\n" \
                      "M0001 N0001 IN001 IN002 VDD PMOS\n" \
                      "M0003 OUT01 N0001 IN002 VDD PMOS\n"
        netlist.set_netlist(str_netlist)
        netlist.remove_transistor("M0003", True)
        str_netlist = "M0001 VDD N0001 N0002 GND NMOS\n" \
                      "M0002 N0001 IN001 IN002 VDD PMOS\n" \
                      "M0003 OUT01 N0001 IN002 VDD PMOS\n"
        self.assertEqual(str_netlist, netlist.get_netlist_string())
        self.assertEqual(len(netlist.p_transistors_), 2)
        self.assertEqual(len(netlist.n_transistors_), 1)

    def test_short_transistor_with_auto_node_removal(self):
        netlist = Netlist()
        str_netlist = "M0001 OUT01 N0001 IN002 VDD PMOS\n"
        netlist.set_netlist(str_netlist)
        self.assertEqual(len(netlist.node_dicts_[netlist.get_set_name_for_node('N0001')]), 1)
        old_gate_name = netlist.turn_on_transistor('M0001')
        self.assertEqual(old_gate_name, 'N0001')
        self.assertEqual(len(netlist.node_dicts_[netlist.get_set_name_for_node('N0001')]), 0)

    def test_short_transistor_without_auto_node_removal(self):
        netlist = Netlist()
        str_netlist = "M0001 VDD N0001 N0002 GND NMOS\n" \
                      "M0002 N0001 IN001 IN002 VDD PMOS\n" \
                      "M0003 OUT01 N0001 IN002 VDD PMOS\n"
        netlist.set_netlist(str_netlist)
        self.assertEqual(len(netlist.node_dicts_[netlist.get_set_name_for_node('N0001')]), 2)
        old_gate_name = netlist.turn_on_transistor('M0001')
        self.assertEqual(old_gate_name, 'N0001')
        self.assertEqual(len(netlist.node_dicts_[netlist.get_set_name_for_node('N0001')]), 2)

    def test_unshort_transistor(self):
        netlist = Netlist()
        str_netlist = "M0001 OUT01 N0001 IN002 VDD PMOS\n"
        netlist.set_netlist(str_netlist)
        self.assertEqual(len(netlist.node_dicts_[netlist.get_set_name_for_node('N0001')]), 1)
        old_gate_name = netlist.turn_on_transistor('M0001')
        self.assertEqual(old_gate_name, 'N0001')
        self.assertEqual(len(netlist.node_dicts_[netlist.get_set_name_for_node('N0001')]), 0)

        netlist.replace_transistor_gate('M0001', old_gate_name)
        self.assertEqual(len(netlist.node_dicts_[netlist.get_set_name_for_node('N0001')]), 1)
        self.assertEqual(str_netlist, netlist.get_netlist_string())

    def test_transistor_gate_diff_same(self):
        netlist = Netlist()
        str_netlist = "M0001 VDD VDD N0002 GND NMOS\n" \
                      "M0002 N0001 IN002 IN002 VDD PMOS\n" \
                      "M0003 OUT01 N0001 IN002 VDD PMOS\n"
        netlist.set_netlist(str_netlist)

        self.assertTrue(netlist.get_transistor('M0001').is_gate_same_as_one_diff())
        self.assertTrue(netlist.get_transistor('M0002').is_gate_same_as_one_diff())
        self.assertFalse(netlist.get_transistor('M0003').is_gate_same_as_one_diff())


if __name__ == '__main__':
    unittest.main()
