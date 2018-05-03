#!/usr/bin/env python3

from tqdm import tqdm
from ArkLibPy.ArkDBMySQL import ArkDBMySQL
from Structural_hypo_checker import *
from Nonminimality_strategy import *


class NonminimalEliminator:
    def __init__(self, db_config, table):
        self.db_ = ArkDBMySQL(db_config_file=db_config)
        self.table_ = table
        self.db_.set_table(self.table_)
        self.hypo_checker_ = StructuralHypoChecker()
        self.hypo_checker_.set_strategy(NonminimalityStrategy())

    def eliminate_nonminimal_cells(self, start, cnt, is_checking_bsf_weak=True):
        query = f'SELECT idCELL, CELL_NETLIST FROM {self.table_} LIMIT {start},{cnt}'
        nonminimal_cell_ids = list()
        runner_idx = start // cnt
        for row in tqdm(self.db_.run_query_get_all_row(query), desc=f'Eliminating nonminimal[{runner_idx:02}]:'):
            self.hypo_checker_.set_netlist(row['CELL_NETLIST'])
            self.hypo_checker_.check()

            if is_checking_bsf_weak:
                is_non_minimal = not self.hypo_checker_.is_all_bsf_weak_diff()
            else:
                is_non_minimal = not self.hypo_checker_.is_all_bsf_diff()

            if is_non_minimal:
                self.db_.delete_nocommit(row['idCELL'], 'idCELL')
                nonminimal_cell_ids.append(row['idCELL'])
        self.db_.commit()
