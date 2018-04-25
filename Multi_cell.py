#!/usr/bin/env python3

from itertools import *
from Cell import *


class MultiCell:
    def __init__(self):
        self.netlist_1_ = Netlist()
        self.netlist_2_ = Netlist()
        self.multi_cell_netlist_ = Netlist()

    @staticmethod
    def get_name_for_cnt(name_group, cnt):
        if name_group == 'in':
            return f'IN{cnt:03}'
        elif name_group == 'internal':
            return f'N{cnt:04}'
        else:
            raise ValueError(f'Unexpected group {name_group}')

    def gen_connect_renaming_dicts(self, target_pi_name, pi_max_cnt_1, internal_max_cnt_2):
        # change it to internal node y+1
        #   for second_cell's all other PIs (e.g., input b), if b<a, then b becomes b+z, otherwise b is b+z-1
        rename_dict = dict()
        restore_dict = dict()
        for pi_name in self.netlist_2_.get_node_names_for_dict('in'):
            if pi_name == target_pi_name:
                rename_dict[pi_name] = self.get_name_for_cnt('internal', internal_max_cnt_2 + 1)
            elif int(pi_name[2:]) < int(target_pi_name[2:]):
                rename_dict[pi_name] = self.get_name_for_cnt('in', int(pi_name[2:]) + pi_max_cnt_1)
            else:
                rename_dict[pi_name] = self.get_name_for_cnt('in', int(pi_name[2:]) + pi_max_cnt_1 - 1)
            restore_dict[rename_dict[pi_name]] = pi_name
        return rename_dict, restore_dict

    def gen_pi_renaming_dicts(self, names, max_cnt_1):
        # change it to internal node y+1
        #   for second_cell's all other PIs (e.g., input b), if b<a, then b becomes b+z, otherwise b is b+z-1
        rename_dict = dict()
        restore_dict = dict()
        idx = 0
        for pi_name in self.multi_cell_netlist_.get_node_names_for_dict('in'):
            # only update PIs for the second cell
            if int(pi_name[2:]) > max_cnt_1:
                rename_dict[pi_name] = names[idx]
                restore_dict[rename_dict[pi_name]] = pi_name
                idx += 1
        return rename_dict, restore_dict

    def construct(self, str_netlist_1, str_netlist_2):
        iso_multi = list()
        shared_multi = list()
        self.netlist_1_.set_netlist(str_netlist_1)
        self.netlist_2_.set_netlist(str_netlist_2)

        # gather first cell's largest internal node number as internal_node_max_cnt_1 = x
        internal_node_max_cnt_1 = self.netlist_1_.get_max_cnt_for_dict('internal')
        # gather first cell's largest Primary Input number as pi_max_cnt_1 = z
        pi_max_cnt_1 = self.netlist_1_.get_max_cnt_for_dict('in')

        # add x to each internal node of the second_cell
        self.netlist_2_.shift_node_cnt_for_dict('internal', internal_node_max_cnt_1)
        # gather second cell's largest internal node number as internal_node_max_cnt_2 = y
        internal_node_max_cnt_2 = self.netlist_2_.get_max_cnt_for_dict('internal')

        if internal_node_max_cnt_2 == 0:
            internal_node_max_cnt_2 = internal_node_max_cnt_1

        # replace first cell's output node to internal node y+1
        self.netlist_1_.rename_node(self.get_name_for_cnt('internal', internal_node_max_cnt_2+1), 'OUT01')

        # update pi names of the second cell to connect two cells together
        # REPEAT for ALL pi in second cell:
        for input_a in self.netlist_2_.get_node_names_for_dict('in'):
            # select one of second_cell's PI (e.g., input a)
            # change it to internal node y+1 and adjust all other inputs of the second cell
            rename_dict, restore_dict = self.gen_connect_renaming_dicts(
                input_a, pi_max_cnt_1, internal_node_max_cnt_2)

            modified_netlist_2 = Netlist()
            modified_netlist_2.set_netlist(self.netlist_2_.get_netlist_string())
            for origin_name, new_name in sorted(rename_dict.items(), reverse=True):
                modified_netlist_2.rename_node(new_name, origin_name)

            # assign inputs for the new multi-cell
            pi_assignments_1 = [self.get_name_for_cnt('in', x)
                                for x in range(1, self.netlist_1_.get_max_cnt_for_dict('in')+1)]
            for pi_assignments_2 in product(('IN001', 'IN002', 'IN003'),
                                            repeat=modified_netlist_2.get_node_cnt_for_dict('in')):
                is_shared = False
                # check if the PI assignment is a shared input case
                if len(set(pi_assignments_1).intersection(set(pi_assignments_2))) != 0 \
                        and len(pi_assignments_2) != 0:
                    is_shared = True

                # merge two cells together into one cell
                self.multi_cell_netlist_.reset_netlist()
                for transistor in self.netlist_1_.get_transistors():
                    self.multi_cell_netlist_.add_transistor(transistor.get_description())
                for transistor in modified_netlist_2.get_transistors():
                    self.multi_cell_netlist_.add_transistor(transistor.get_description())
                self.multi_cell_netlist_.update_transistor_names()

                # assign inputs for the second cell
                pi_rename_dict, pi_restore_dict = self.gen_pi_renaming_dicts(pi_assignments_2, pi_max_cnt_1)
                for origin_name, new_name in sorted(pi_rename_dict.items(), reverse=True):
                    self.multi_cell_netlist_.rename_node_only(new_name, origin_name)

                # find cell in library and label it
                if is_shared:
                    shared_multi.append(self.multi_cell_netlist_.get_netlist_string())
                else:
                    iso_multi.append(self.multi_cell_netlist_.get_netlist_string())

        return iso_multi, shared_multi
