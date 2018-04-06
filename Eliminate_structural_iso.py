#!/usr/bin/env python3

from tqdm import tqdm
from Circuit.Netlist import *
from ArkLibPy.ArkDBMySQL import ArkDBMySQL


class ISOEliminator:
    def __init__(self, db_config, table):
        self.db_ = ArkDBMySQL(db_config_file=db_config)
        self.table_ = table
        self.db_.set_table(self.table_)
        self.netlist_ = Netlist()

    def get_iso_cell_ids_based_on_id(self, id_cell, bsf_unified):
        src_netlist = self.db_.get_query_value('CELL_NETLIST',
                                               f'SELECT CELL_NETLIST FROM {self.table_} WHERE idCELL=%s',
                                               [id_cell])
        self.netlist_.set_netlist(src_netlist)
        query = f'SELECT Q.ID FROM '\
                '(SELECT idCELL AS ID, CELL_NETLIST AS Netlist FROM {self.table_} WHERE CELL_BSF_UNIFIED=%s)'\
                ' AS Q WHERE Q.Netlist IN ('
        temp = "', '".join(self.netlist_.get_equ_netlists())
        temp = "'" + temp + "'"
        query += temp
        query += ')'

        id_list = list()
        for row in self.db_.run_query(query, [bsf_unified]):
            if int(row['ID']) != int(id_cell):
                id_list.append(int(row['ID']))

        return id_list

    def eliminate_iso(self):
        query = f'SELECT DISTINCT CELL_BSF_UNIFIED FROM {self.table_}'
        bsf_uni_list = list()
        for row in self.db_.run_query_get_all_row(query):
            bsf_uni_list.append(row['CELL_BSF_UNIFIED'].decode("utf-8"))

        for bsf in tqdm(bsf_uni_list, desc='Eliminating: '):
            query = f'SELECT idCELL FROM {self.table_} WHERE CELL_BSF_UNIFIED=%s'
            id_list = list()
            removed_ids = set()
            for row in self.db_.run_query_get_all_row(query, [bsf]):
                id_list.append(row['idCELL'])
            for id_cell in tqdm(id_list, desc=f'Cells in {bsf}: '):
                if id_cell in removed_ids:
                    continue
                dup_ids = self.get_iso_cell_ids_based_on_id(id_cell, bsf)
                removed_ids.update(dup_ids)
                if len(dup_ids) != 0:
                    str_temp = ', '.join([str(x) for x in dup_ids])
                    query = f'DELETE FROM {self.table_} WHERE idCELL IN ({str_temp})'
                    self.db_.run_sql(query)
        self.db_.optimize()
