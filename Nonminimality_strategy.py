#!/usr/bin/env python3


class NonminimalityStrategy:
    def __init__(self):
        self.netlist = None

    def get_str_netlists(self, netlist):
        self.netlist = netlist
        if self.netlist.get_transistors_cnt() <= 1:
            return []
        for i in range(1, self.netlist.get_transistors_cnt()+1):
            transistor = self.netlist.remove_transistor(f'M{i:04}', False)
            yield self.netlist.get_netlist_string()
            self.netlist.add_transistor(transistor.get_description())
