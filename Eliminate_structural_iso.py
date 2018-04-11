#!/usr/bin/env python3

from tqdm import tqdm
from Circuit.Netlist import *
from ArkLibPy.ArkDBMySQL import ArkDBMySQL
from Cell import *


class ISOEliminator:
    def __init__(self, db_config, table):
        self.db_ = ArkDBMySQL(db_config_file=db_config)
        self.table_ = table
        self.db_.set_table(self.table_)
        self.cell_ = Cell(self.db_)

    def get_iso_cell_ids_based_on_id(self, id_cell):
        self.cell_.init_based_on_id(id_cell)
        id_list = self.cell_.fetch_ids()
        id_list.remove(id_cell)
        return id_list

    def eliminate_iso(self, start, cnt):
        query = f'SELECT DISTINCT CELL_BSF_UNIFIED FROM {self.table_} LIMIT {start},{cnt}'
        bsf_uni_list = list()
        for row in self.db_.run_query_get_all_row(query):
            bsf_uni_list.append(row['CELL_BSF_UNIFIED'].decode("utf-8"))

        runner_idx = start // cnt
        for bsf in tqdm(bsf_uni_list, desc=f'Eliminating str iso[{runner_idx:02}]:'):
            query = f'SELECT idCELL FROM {self.table_} WHERE CELL_BSF_UNIFIED=%s'
            id_list = list()
            removed_ids = set()
            for row in self.db_.run_query_get_all_row(query, [bsf]):
                id_list.append(row['idCELL'])
            for id_cell in tqdm(id_list, desc=f'Cells in {bsf}: '):
                if id_cell in removed_ids:
                    continue
                dup_ids = self.get_iso_cell_ids_based_on_id(id_cell)
                removed_ids.update(dup_ids)
                if len(dup_ids) != 0:
                    str_temp = ', '.join([str(x) for x in dup_ids])
                    query = f'DELETE FROM {self.table_} WHERE idCELL IN ({str_temp})'
                    self.db_.run_sql_nocommit(query)
