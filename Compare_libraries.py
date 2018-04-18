#!/usr/bin/env python3

from Cell import *


class CompareLibraries:
    def __init__(self, db_config, table):
        self.db_ = ArkDBMySQL(db_config_file=db_config)
        self.table_ = table
        self.db_.set_table(self.table_)

    @staticmethod
    def is_known_case(str_netlist):
        netlist = Netlist()
        netlist.set_netlist(str_netlist)
        for transistor in netlist.get_transistors():
            if transistor.is_gate_same_as_one_diff():
                return True
        return False

    def is_subset_of(self, superset_table):
        query = f'SELECT idCELL, CELL_NETLIST FROM {superset_table}'
        cell = Cell(self.db_)

        not_found_list = list()
        for row in tqdm(self.db_.run_query_get_all_row(query),
                        desc=f'Checking if {superset_table} has all cells from {self.table_}:'):
            if self.is_known_case(row['CELL_NETLIST']):
                continue
            cell.init_based_on_netlist(row['CELL_NETLIST'])
            id_list = cell.fetch_ids()
            if len(id_list) == 0:
                not_found_list.append(row['idCELL'])

        for id_cell in not_found_list:
            print(f'cell #{id_cell} not found in {self.table_}')
