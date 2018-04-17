#!/usr/bin/env python3


class NonminimalityStrategy:
    def __init__(self):
        self.netlist = None

    def get_str_netlists(self, netlist):
        self.netlist = netlist
        if self.netlist.get_transistors_cnt() <= 1:
            return []
        self.netlist.update_transistor_names()

        for i in range(1, self.netlist.get_transistors_cnt()+1):
            # generate netlists for open cases
            transistor = self.netlist.remove_transistor(f'M{i:04}', False)
            yield self.netlist.get_netlist_string()
            self.netlist.add_transistor(transistor.get_description())

            # generate netlists for short cases
            origin_gate_name = self.netlist.turn_on_transistor(f'M{i:04}')
            yield self.netlist.get_netlist_string()
            self.netlist.replace_transistor_gate(f'M{i:04}', origin_gate_name)
