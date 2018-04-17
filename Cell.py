#!/usr/bin/env python3

from Circuit.Netlist import *
from Circuit.CSim import *
from bsf import *


class Cell:
    def __init__(self, db):
        self.netlist_ = Netlist()
        self.upstream_db_ = db
        self.cell_id_ = None
        self.bsf_ = None
        self.bsf_weak_ = None
        self.bsf_unified_ = None
        self.bsf_weak_unified_ = None

    def init_based_on_id(self, id_cell):
        self.cell_id_ = id_cell
        self.bsf_ = None
        self.bsf_weak_ = None
        self.bsf_unified_ = None
        self.bsf_weak_unified_ = None
        row = self.upstream_db_.get_query_row('SELECT CELL_BSF, CELL_BSF_UNIFIED, CELL_BSF_weak, '
                                              'CELL_BSF_weak_UNIFIED, CELL_NETLIST '
                                              f'FROM {self.upstream_db_.table_} WHERE idCELL=%s',
                                                        [id_cell])
        if row is None:
            raise ValueError(f'Cell #{id_cell} not found in {self.upstream_db_.table_}')
        self.netlist_.set_netlist(row['CELL_NETLIST'])
        self.bsf_ = row['CELL_BSF'].decode("utf-8")
        self.bsf_weak_ = row['CELL_BSF_weak'].decode("utf-8")
        self.bsf_unified_ = row['CELL_BSF_UNIFIED'].decode("utf-8")
        self.bsf_weak_unified_ = row['CELL_BSF_weak_UNIFIED'].decode("utf-8")

    def init_based_on_netlist(self, netlist):
        self.cell_id_ = None
        self.bsf_ = None
        self.bsf_weak_ = None
        self.bsf_unified_ = None
        self.bsf_weak_unified_ = None
        self.netlist_.set_netlist(netlist)

    def cal_bsf(self):
        self.bsf_, self.bsf_weak_ = csim(self.netlist_.get_netlist_string())

        self.bsf_unified_, bsf_list = gen_equ_bsf(self.bsf_)
        self.bsf_weak_unified_, bsf_list = gen_equ_bsf(self.bsf_weak_)

    def get_upstream_db(self):
        return self.upstream_db_

    def set_upstream_db(self, db_):
        self.upstream_db_ = db_

    def get_bsf(self):
        if not self.bsf_:
            self.cal_bsf()
        return self.bsf_

    def get_bsf_unified(self):
        if not self.bsf_unified_:
            self.cal_bsf()
        return self.bsf_unified_

    def get_bsf_weak(self):
        if not self.bsf_weak_:
            self.cal_bsf()
        return self.bsf_weak_

    def fetch_ids(self):
        query = f'SELECT Q.ID FROM ' \
                f'(SELECT idCELL AS ID, CELL_NETLIST AS Netlist ' \
                f'FROM {self.upstream_db_.get_table()} WHERE CELL_BSF_UNIFIED=%s)' \
                f' AS Q WHERE Q.Netlist IN ('
        temp = "', '".join(self.netlist_.get_equ_netlists())
        temp = "'" + temp + "'"
        query += temp
        query += ')'

        id_list = list()
        for row in self.upstream_db_.run_query(query, [self.get_bsf_unified()]):
            id_list.append(int(row['ID']))

        return id_list

    def get_id(self):
        if self.cell_id_ is None:
            id_list = self.fetch_ids()
            if id_list:
                self.cell_id_ = id_list[0]
            else:
                self.cell_id_ = 0
        return self.cell_id_
