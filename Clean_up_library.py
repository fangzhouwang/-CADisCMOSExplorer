#!/usr/bin/env python3

from joblib import Parallel, delayed
import multiprocessing
import sys

from Eliminate_structural_iso import *
from Eliminate_nonminimal import *
from Compare_libraries import *
from Multi_cell import *
from ArkLibPy.ArkDBMySQL import ArkDBMySQL
from ULM_cell import *


# Utility functions

# --- Support parallelism
def get_num_cores():
    num_cores = multiprocessing.cpu_count() - 2
    if num_cores < 1:
        num_cores = 1
    return num_cores


def gen_limits(total_cnt, n_jobs):
    ret = list()
    if total_cnt < n_jobs:
        size = 1
        remain = 0
    else:
        size = total_cnt // n_jobs
        remain = total_cnt - size * n_jobs

    for start in range(0, total_cnt-remain, size):
        ret.append([start, size])
    else:
        # add the remain number to the last item in the list
        ret[-1][1] += remain

    if total_cnt < n_jobs:
        for i in range(n_jobs-total_cnt):
            ret.append([0, 0])

    return ret


def prepare(db_config, query, n_jobs):
    db = ArkDBMySQL(db_config_file=db_config)
    item_cnt = db.get_query_value('CNT', query)
    return gen_limits(item_cnt, n_jobs)


# --- Database related helper functions
def create_indexes(db_config, table, index_list):
    db = ArkDBMySQL(db_config_file=db_config)
    db.set_table(table)
    for index in index_list:
        db.add_index(index)


def remove_indexes(db_config, table, index_list):
    db = ArkDBMySQL(db_config_file=db_config)
    db.set_table(table)
    for index in index_list:
        db.remove_index(index)


def get_cell_cnt(db_config, table):
    db = ArkDBMySQL(db_config_file=db_config)
    query = f'SELECT COUNT(*) AS CNT FROM {table} WHERE CELL_PMOS_CNT+CELL_NMOS_CNT=%s'
    ret = dict()
    for i in range(1, 6):
        ret[i] = db.get_query_value('CNT', query, [i])
    return ret


# Cleaning procedures

def duplicate_table(db_config, new_table, source_table, copy_indexes_n_triggers=True):
    db = ArkDBMySQL(db_config_file=db_config)
    if db.is_table_exist(new_table):
        print(f'table {new_table} already exists')
        return
    if copy_indexes_n_triggers:
        query = f'CREATE TABLE {new_table} LIKE {source_table}'
        db.run_sql(query)
        if db.get_error():
            exit(1)
        query = f'INSERT {new_table} SELECT * FROM {source_table}'
        db.run_sql(query)
        if db.get_error():
            exit(1)
    else:
        query = f'CREATE TABLE {new_table} AS SELECT * FROM {source_table}'
        db.run_sql(query)
        if db.get_error():
            exit(1)


def remove_constant(db_config, table):
    db = ArkDBMySQL(db_config_file=db_config)
    query = f'DELETE FROM {table} WHERE CELL_BSF_UNIFIED=%s'
    db.run_sql(query, ['0'])
    db.run_sql(query, ['1'])

    print(get_cell_cnt(db_config, table))


def remove_redundant_input(db_config, table):
    db = ArkDBMySQL(db_config_file=db_config)
    query = f'DELETE FROM {table} WHERE length(CELL_BSF) > length(CELL_BSF_UNIFIED)'
    db.run_sql(query)

    print(get_cell_cnt(db_config, table))


def process_remove_isomorphic(db_config, table, limit):
    if limit[1] == 0:
        return
    elm = ISOEliminator(db_config, table)
    elm.eliminate_iso(limit[0], limit[1])


def remove_isomorphic(db_config, table, num_cores):
    Parallel(n_jobs=num_cores)(delayed(process_remove_isomorphic)(db_config, table, i)
         for i in prepare(db_config, f'SELECT COUNT(DISTINCT CELL_BSF_UNIFIED) AS CNT FROM {table}', num_cores))
    print(get_cell_cnt(db_config, table))


def process_remove_nonminimal(db_config, table, limit):
    if limit[1] == 0:
        return
    elm = NonminimalEliminator(db_config, table)
    elm.eliminate_nonminimal_cells(limit[0], limit[1])


def remove_nonminimal(db_config, table, num_cores):
    Parallel(n_jobs=num_cores)(delayed(process_remove_nonminimal)(db_config, table, i)
                               for i in prepare(db_config, f'SELECT count(*) AS CNT FROM {table}', num_cores))
    print(get_cell_cnt(db_config, table))


def process_update_bsf_uni(bsf_col, db_config, table, limit):
    if limit[1] == 0:
        return
    update_bsf_uni_for_table(bsf_col, db_config, table, limit[0], limit[1])


def update_bsf_uni(bsf_col, db_config, table, num_cores):
    Parallel(n_jobs=num_cores)(delayed(process_update_bsf_uni)(bsf_col, db_config, table, i)
                               for i in prepare(db_config, f'SELECT count(*) AS CNT FROM BSF_LIB', num_cores))


def tag_multi_cell(db_config, table):
    db = ArkDBMySQL(db_config_file=db_config)
    db.set_table(table)
    cell = Cell(db)

    # select all 1~3 tx cells
    netlists = [
        row['CELL_NETLIST'] for row in
        db.run_query_get_all_row(f'SELECT CELL_NETLIST FROM {db.get_table()} WHERE CELL_PMOS_CNT+CELL_NMOS_CNT<=2')
    ]

    # for every two of them, construct multi-cells
    for two_netlists in tqdm(list(product(netlists, repeat=2)), desc='Multi-cell'):
        multi_cell = MultiCell()
        iso_multi, shared_multi = multi_cell.construct(two_netlists[0], two_netlists[1])

        # search for those multi-cells in lib and tag them
        for str_netlist in iso_multi:
            cell.init_based_on_netlist(str_netlist)
            cell.add_to_family('MultiCellIsoInput')
        for str_netlist in shared_multi:
            cell.init_based_on_netlist(str_netlist)
            cell.add_to_family('MultiCellSharedInput')


def tag_ulm_cell(db_config, table):
    db = ArkDBMySQL(db_config_file=db_config)
    db.set_table(table)

    ulm_cell = ULMCell()
    cell = Cell(db)

    for netlist in tqdm(list(ulm_cell.construct_ulm_cells()), desc='ULM-cell'):
        # search for those ulm-cells in lib and tag them
        cell.init_based_on_netlist(netlist)
        cell.add_to_family('ULM')

    for netlist in tqdm(list(ulm_cell.construct_ulm_inv_polarity_cells()), desc='ULM_inv_pol-cell'):
        cell.init_based_on_netlist(netlist)
        cell.add_to_family('ULM_INV_POL')


def tag_extended_ulm_cell(db_config, table):
    db = ArkDBMySQL(db_config_file=db_config)
    db.set_table(table)

    ulm_cell = ULMCell()
    cell = Cell(db)

    for netlist in tqdm(list(ulm_cell.construct_extended_ulm_cells()), desc='EXT-ULM-cell'):
        # search for those ulm-cells in lib and tag them
        cell.init_based_on_netlist(netlist)
        cell.add_to_family('EXT_ULM')

    for netlist in tqdm(list(ulm_cell.construct_extended_ulm_inv_polarity_cells()), desc='EXT-ULM_inv_pol-cell'):
        cell.init_based_on_netlist(netlist)
        cell.add_to_family('EXT_ULM_INV_POL')


def remove_non_shared_multi_cells(db_config, table):
    db = ArkDBMySQL(db_config_file=db_config)
    db.set_table(table)
    id_list = [
        row['idCELL'] for row in
        db.run_query_get_all_row(f"SELECT idCELL FROM {db.get_table()} WHERE CELL_FAMILY like '%MultiCellIsoInput%'")
    ]
    for id_cell in id_list:
        db.delete(id_cell, 'idCELL')
    if len(id_list) != 0:
        db.commit()
    print(get_cell_cnt(db_config, table))


def process_remove_nonminimal_strong(db_config, table, limit):
    if limit[1] == 0:
        return
    elm = NonminimalEliminator(db_config, table)
    elm.eliminate_nonminimal_cells(limit[0], limit[1], False)


def remove_nonminimal_strong(db_config, table, num_cores):
    Parallel(n_jobs=num_cores)(delayed(process_remove_nonminimal_strong)(db_config, table, i)
                               for i in prepare(db_config, f'SELECT count(*) AS CNT FROM {table}', num_cores))
    print(get_cell_cnt(db_config, table))


def clean_up(db_config, table, source='RAW_DATA_LIB'):
    print(f'--- duplicating {source} as {table} ---')
    duplicate_table(db_config, table, source)

    print('--- creating indexes ---')
    create_indexes(db_config, table, [
        'CELL_PMOS_CNT',
        'CELL_NMOS_CNT',
        'CELL_NETLIST',
        'CELL_BSF',
        'CELL_BSF_weak'
    ])

    print('--- number of cells before cleaning up ---')
    print(get_cell_cnt(db_config, table))

    print('--- updating bsf_unified ---')
    update_bsf_uni('CELL_BSF', db_config, table, get_num_cores())

    print('--- removing constant cells ---')
    remove_constant(db_config, table)
    print('--- removing cells with redundant inputs ---')
    remove_redundant_input(db_config, table)

    print('--- updating bsf_weak_unified ---')
    update_bsf_uni('CELL_BSF_weak', db_config, table, get_num_cores())
    create_indexes(db_config, table, [
        'CELL_BSF_UNIFIED',
        'CELL_BSF_weak_UNIFIED'
    ])

    print('--- removing isomorphic cells ---')
    remove_isomorphic(db_config, table, get_num_cores())

    print('--- removing nonminimal cells ---')
    remove_nonminimal(db_config, table, get_num_cores())

    print('--- tagging multi cells ---')
    tag_multi_cell(db_config, table)

    print('--- removing non-shared multi cells ---')
    remove_non_shared_multi_cells(db_config, table)

    print('--- tagging ULM cells ---')
    tag_ulm_cell(db_config, table)

    print('--- tagging EXT ULM cells ---')
    tag_extended_ulm_cell(db_config, table)
    # print('---  ---')

    # check inclusive
    comp = CompareLibraries(db_config, table)
    comp.is_subset_of('WORK_LIB')


if __name__ == '__main__':
    if sys.platform == 'linux':
        local_db_config = '/home/fangzhou/.db_configs/db_config_local_cadis.txt'
    elif sys.platform == 'darwin':
        local_db_config = '/Users/Ark/.db_configs/db_config_local_cadis.txt'
    else:
        local_db_config = 'ERROR'
        print(f'Error: DB_Config is not setup for {sys.platform} yet.')
        exit(1)

    clean_up(local_db_config, 'NON_MINI_TEST')
