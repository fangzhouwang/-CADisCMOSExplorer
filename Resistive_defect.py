#!/usr/bin/env python3

from Circuit.Netlist import *
from itertools import *
from Circuit.CSim import *


class ResistiveDefect:
    def __init__(self, db):
        self.netlist_ = Netlist()
        self.tg_netlist_ = Netlist()
        self.short_defects_ = list()
        self.open_defects_ = list()
        self.bsf_ = None
        self.bsf_weak_ = None
        self.faulty_bsf_ = None
        self.faulty_bsf_weak_ = None

        self.db_ = db.dup_self()
        self.cell_table_ = db.get_table()
        self.defect_table_ = self.cell_table_ + '_FAULT_LIB'
        if not self.db_.is_table_exist(self.defect_table_):
            self.create_fault_lib()
        self.db_.set_table(self.defect_table_)

    def create_fault_lib(self, is_drop_exist=False):
        table_desc = dict()
        table_desc['table_name'] = self.defect_table_
        table_columns = list()
        table_columns.append({'name': 'idFAULT_LIB', 'type': 'INT', 'property': 'NOT NULL AUTO_INCREMENT'})
        table_columns.append({'name': 'idCELL', 'type': 'INT', 'property': 'NOT NULL'})
        table_columns.append({'name': 'FAULT_DESC', 'type': 'VARCHAR(1000)', 'property': 'NULL'})
        table_columns.append({'name': 'FAULTY_NETLIST', 'type': 'VARCHAR(1000)', 'property': 'NULL'})
        table_columns.append({'name': 'FAULTY_BSF', 'type': 'VARCHAR(256)',
                              'property': "CHARACTER SET 'utf8' COLLATE 'utf8_bin' NULL"})
        table_columns.append({'name': 'FAULTY_BSF_weak', 'type': 'VARCHAR(256)',
                              'property': "CHARACTER SET 'utf8' COLLATE 'utf8_bin' NULL"})
        table_columns.append({'name': 'FAULT_TYPE', 'type': 'VARCHAR(45)', 'property': 'NULL'})
        table_columns.append({'name': 'FAULTY_VEC_CNT', 'type': 'INT', 'property': 'NULL'})
        table_columns.append({'name': 'FAULTY_VEC_CNT_weak', 'type': 'INT', 'property': 'NULL'})

        table_desc['table_columns'] = table_columns
        table_primary_keys = ['idFAULT_LIB']
        table_desc['table_pks'] = table_primary_keys

        if self.db_.is_table_exist(table_desc['table_name']):
            if is_drop_exist:
                self.db_.run_sql(f"DROP TABLE IF EXISTS {table_desc['table_name']}")
            else:
                return
        self.db_.create_table(table_desc)

    def set_netlist(self, str_netlist):
        self.netlist_.set_netlist(str_netlist)
        self.bsf_, self.bsf_weak_ = csim(str_netlist)
        self.short_defects_.clear()
        self.open_defects_.clear()

    def reset_tg_netlist(self):
        self.tg_netlist_.set_netlist("M1001 IN101 VDD IN102 GND NMOS\nM1002 IN101 GND IN102 VDD PMOS\n")

    def gen_short_defect_str_netlist(self, short_defect):
        self.reset_tg_netlist()
        self.tg_netlist_.rename_node_only(short_defect[0], 'IN101')
        self.tg_netlist_.rename_node_only(short_defect[1], 'IN102')

        return self.netlist_.get_netlist_string() + self.tg_netlist_.get_netlist_string()

    def get_faulty_vec_cnts(self):
        faulty_vec_cnt = 0
        faulty_weak_vec_cnt = 0
        for i in range(len(self.bsf_)):
            if self.bsf_[i] != self.faulty_bsf_[i]:
                faulty_vec_cnt += 1
            if self.bsf_weak_[i] != self.faulty_bsf_weak_[i]:
                faulty_weak_vec_cnt += 1
        return faulty_vec_cnt, faulty_weak_vec_cnt

    def get_defect_info_dict(self, defect, defect_type):
        defect_info_dict = dict()
        defect_info_dict['FAULT_TYPE'] = defect_type
        defect_info_dict['FAULT_DESC'] = str(defect)
        if defect_type == 'open':
            defect_info_dict['FAULTY_NETLIST'] = self.gen_open_defect_str_netlist(defect)
        elif defect_type == 'short':
            defect_info_dict['FAULTY_NETLIST'] = self.gen_short_defect_str_netlist(defect)
        else:
            raise ValueError(f'unknown defect type: {defect_type}')

        self.faulty_bsf_, self.faulty_bsf_weak_ = csim(defect_info_dict['FAULTY_NETLIST'])
        defect_info_dict['FAULTY_BSF'] = self.faulty_bsf_
        defect_info_dict['FAULTY_BSF_weak'] = self.faulty_bsf_weak_
        defect_info_dict['FAULTY_VEC_CNT'], defect_info_dict['FAULTY_VEC_CNT_weak'] = self.get_faulty_vec_cnts()
        return defect_info_dict

    def get_all_defect_info_dicts(self):
        self.gen_defect_list()
        defects_info_list = list()

        for open_defect in self.open_defects_:
            defects_info_list.append(self.get_defect_info_dict(open_defect, 'open'))
        for short_defect in self.short_defects_:
            defects_info_list.append(self.get_defect_info_dict(short_defect, 'short'))

        return defects_info_list

    def insert_defect_details_for_id_cell(self, id_cell):
        str_netlist = self.db_.get_query_value('CELL_NETLIST',
                                               f'SELECT CELL_NETLIST FROM {self.cell_table_} WHERE idCELL=%s',
                                               [id_cell])
        if str_netlist is None:
            raise ValueError(f'Cell # {id_cell} does not exist in {self.cell_table_}')
        self.set_netlist(str_netlist)

        for defect_dict in self.get_all_defect_info_dicts():
            defect_dict['idCELL'] = id_cell
            self.db_.insert_nocommit(defect_dict)

        self.db_.commit()

    def gen_open_defect_str_netlist(self, open_defect):
        defect_node_name = 'N1000'

        self.reset_tg_netlist()
        self.tg_netlist_.rename_node_only(open_defect[0], 'IN101')
        self.tg_netlist_.rename_node_only(defect_node_name, 'IN102')

        # insert defect
        for terminal in open_defect[1]:
            defect_transistor = self.netlist_.get_transistor(terminal[:-1])
            defect_terminal = defect_transistor.get_terminal_with_short_type(terminal[-1:])
            defect_terminal.set_node(self.netlist_.get_node(defect_node_name))

        # save defect netlist
        defect_str_netlist = self.netlist_.get_netlist_string() + self.tg_netlist_.get_netlist_string()

        # restore netlist
        for terminal in open_defect[1]:
            defect_transistor = self.netlist_.get_transistor(terminal[:-1])
            defect_terminal = defect_transistor.get_terminal_with_short_type(terminal[-1:])
            defect_terminal.set_node(self.netlist_.get_node(open_defect[0]))

        return defect_str_netlist

    def gen_defect_list(self):
        nodes = list(self.netlist_.get_all_nodes())

        # short defects
        # a pair of nets
        # E.g. ('GND', 'N0001')
        for node_pair in combinations(nodes, r=2):
            if node_pair[0].is_supply() and node_pair[1].is_supply():
                continue
            if node_pair[0].is_pi() and node_pair[1].is_supply():
                continue
            if node_pair[0].is_supply() and node_pair[1].is_pi():
                continue
            if node_pair[0].is_pi() and node_pair[1].is_pi():
                continue
            self.short_defects_.append((node_pair[0].get_name(), node_pair[1].get_name()))

        # open defects
        # net name followed by
        # 1) either lists of transistor terminals (if the net is a supply net)
        # E.g. ['GND', ['M0001d', 'M0002d', 'M0003d']] will become:
        #       ['GND', ['M0001d']]
        #       ['GND', ['M0002d']]
        #       ['GND', ['M0003d']]
        #
        # 2) (if the net is an internal net or output net)
        # or the first partition of transistor terminals which should be disconnected from the node
        # E.g.  ['N0001', ['M0002s', 'M0003s'], ['M0001g', 'M0005s']] will become:
        #       ['N0001', ['M0002s', 'M0003s']]
        for node in nodes:
            if node.is_pi() or node.is_supply():
                # each terminal can be disconnected from the source/supply net individually
                for terminal in node.get_terminals():
                    temp_defect = list()
                    temp_defect.append(node.get_name())
                    temp_defect.append([terminal.get_owner_name()+terminal.get_type_short()])
                    self.open_defects_.append(temp_defect)
            else:
                # partition needed for internal nodes and output node
                num = len(node.get_terminals())
                if num == 1:
                    # this node only has one terminal hence cannot become open
                    continue
                else:
                    for i in range(1, num):
                        for partitions in combinations(node.get_terminals(), r=i):
                            partition_a = [x.get_owner_name()+x.get_type_short()
                                           for x in node.get_terminals() if x in partitions]
                            temp_defect = list()
                            temp_defect.append(node.get_name())
                            temp_defect.append(partition_a)
                            self.open_defects_.append(temp_defect)
