#!/usr/bin/env python3

from Circuit.Netlist import Netlist
from itertools import *


class ULMCell:
    input_options = [
        'VDD',
        'GND',
        'IN001',
        'IN002',
        'IN003'
    ]
    templates = [
        # INV structure
        "M0001 IN101 IN001 OUT01 GND NMOS\n"
        "M0002 IN102 IN001 OUT01 VDD PMOS\n",

        # NAND structure
        "M0001 OUT01 IN001 N0001 GND NMOS\n"
        "M0002 IN101 IN002 N0001 GND NMOS\n"
        "M0003 IN102 IN001 OUT01 VDD PMOS\n"
        "M0004 IN102 IN002 OUT01 VDD PMOS\n",

        # NOR structure
        "M0001 IN101 IN001 OUT01 GND NMOS\n"
        "M0002 IN101 IN002 OUT01 GND NMOS\n"
        "M0003 IN102 IN001 N0001 VDD PMOS\n"
        "M0004 OUT01 IN002 N0001 VDD PMOS\n"
    ]

    def __init__(self):
        self.netlist = Netlist()

    def construct_cells_from_ulm_template(self, template):
        self.netlist.set_netlist(template)
        max_cnt = self.netlist.get_max_cnt_for_dict('in')
        max_cnt -= 100

        for inputs in product(self.input_options, repeat=max_cnt):
            self.netlist.set_netlist(template)
            for i in range(0, max_cnt):
                self.netlist.rename_node_only(inputs[i], Netlist.get_name_for_cnt('in', i+101))
            yield self.netlist.get_netlist_string()

    def construct_ulm_cells(self):
        for template in self.templates:
            for str_netlist in self.construct_cells_from_ulm_template(template):
                yield str_netlist

    def construct_ulm_inv_polarity_cells(self):
        for str_netlist in self.construct_ulm_cells():
            for inv_polarity_str_netlist in self.construct_ulm_inv_polarity_cells_from_strnetlist(str_netlist):
                yield inv_polarity_str_netlist

    @staticmethod
    def construct_ulm_inv_polarity_cells_from_strnetlist(str_netlist):
        netlist = Netlist()
        netlist.set_netlist(str_netlist)
        gate_pi_max_cnt = netlist.get_max_cnt_for_dict('in')

        flip_transistors = list()

        # gate_pi_max_cnt+1 is not included because if all PIs are flipped
        # then it refers to and will be covered by another template
        for flip_cnt in range(1, gate_pi_max_cnt):
            for flip_pi_list in combinations(
                    [Netlist.get_name_for_cnt('in', x) for x in range(1, gate_pi_max_cnt+1)], r=flip_cnt):

                flip_transistors.clear()
                # gather all transistors to be flipped
                for pi_name in flip_pi_list:
                    for transistor in netlist.get_transistors_with_node_to_term(pi_name, 'gate'):
                        flip_transistors.append(transistor)

                # flip transistors, generate str_netlist, and then restore those transistors
                for transistor in flip_transistors:
                    netlist.flip_transistor_type(transistor)
                netlist.update_transistor_names()
                yield netlist.get_netlist_string()
                for transistor in flip_transistors:
                    netlist.flip_transistor_type(transistor)
                netlist.update_transistor_names()
