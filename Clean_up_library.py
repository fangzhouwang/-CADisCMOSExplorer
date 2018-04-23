#!/usr/bin/env python3

from joblib import Parallel, delayed
import multiprocessing
import sys

from Eliminate_structural_iso import *
from Eliminate_nonminimal import *
from Compare_libraries import *


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
def create_indexes(table, db_config, index_list):
    db = ArkDBMySQL(db_config_file=db_config)
    db.set_table(table)
    for index in index_list:
        db.add_index(index)


def remove_indexes(table, db_config, index_list):
    db = ArkDBMySQL(db_config_file=db_config)
    db.set_table(table)
    for index in index_list:
        db.remove_index(index)


def get_cell_cnt(table, db_config):
    db = ArkDBMySQL(db_config_file=db_config)
    query = f'SELECT COUNT(*) AS CNT FROM {table} WHERE CELL_PMOS_CNT+CELL_NMOS_CNT=%s'
    ret = dict()
    for i in range(1, 6):
        ret[i] = db.get_query_value('CNT', query, [i])
    return ret


# Cleaning procedures

def duplicate_table(new_table, source_table, db_config, copy_indexes_n_triggers=True):
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


"""
def show_constant(table, db_config):
    db = ArkDBMySQL(db_config_file=db_config)
    query = f"SELECT * FROM {table} WHERE CELL_BSF_UNIFIED=%s AND CELL_PMOS_CNT+CELL_NMOS_CNT <=2"
    print('--- 0 ---')
    res = db.run_query_get_all_row(query, ['0'])
    for row in res:
        print(f"{row['idCELL']} {row['CELL_BSF']} {row['CELL_BSF_UNIFIED']}")
    print('--- 1 ---')
    res = db.run_query_get_all_row(query, ['1'])
    for row in res:
        print(f"{row['idCELL']} {row['CELL_BSF']} {row['CELL_BSF_UNIFIED']}")

    print(get_cell_cnt(table, db_config))
"""


def remove_constant(table, db_config):
    db = ArkDBMySQL(db_config_file=db_config)
    query = f'DELETE FROM {table} WHERE CELL_BSF_UNIFIED=%s'
    db.run_sql(query, ['0'])
    db.run_sql(query, ['1'])

    print(get_cell_cnt(table, db_config))


def remove_redundant_input(table, db_config):
    db = ArkDBMySQL(db_config_file=db_config)
    query = f'DELETE FROM {table} WHERE length(CELL_BSF) > length(CELL_BSF_UNIFIED)'
    db.run_sql(query)

    print(get_cell_cnt(table, db_config))


def process_remove_isomorphic(db_config, table, limit):
    if limit[1] == 0:
        return
    elm = ISOEliminator(db_config, table)
    elm.eliminate_iso(limit[0], limit[1])


def remove_isomorphic(table, db_config, num_cores):
    Parallel(n_jobs=num_cores)(delayed(process_remove_isomorphic)(db_config, table, i)
         for i in prepare(db_config, f'SELECT COUNT(DISTINCT CELL_BSF_UNIFIED) AS CNT FROM {table}', num_cores))
    print(get_cell_cnt(table, db_config))


def process_remove_nonminimal(db_config, table, limit):
    if limit[1] == 0:
        return
    elm = NonminimalEliminator(db_config, table)
    elm.eliminate_nonminimal_cells(limit[0], limit[1])


def remove_nonminimal(table, db_config, num_cores):
    Parallel(n_jobs=num_cores)(delayed(process_remove_nonminimal)(db_config, table, i)
         for i in prepare(db_config, f'SELECT count(*) AS CNT FROM {table}', num_cores))
    print(get_cell_cnt(table, db_config))


def process_update_bsf_uni(bsf_col, db_config, table, limit):
    if limit[1] == 0:
        return
    update_bsf_uni_for_table(bsf_col, table, db_config, limit[0], limit[1])


def update_bsf_uni(bsf_col, table, db_config, num_cores):
    Parallel(n_jobs=num_cores)(delayed(process_update_bsf_uni)(bsf_col, db_config, table, i)
                               for i in prepare(db_config, f'SELECT count(*) AS CNT FROM BSF_LIB', num_cores))


def clean_up(table, db_config, source='RAW_DATA_LIB'):
    # print('---  ---')
    print(f'--- duplicating {source} as {table} ---')
    duplicate_table(table, source, db_config)

    print('--- creating indexes ---')
    create_indexes(table, db_config, [
        'CELL_PMOS_CNT',
        'CELL_NMOS_CNT',
        'CELL_NETLIST',
        'CELL_BSF',
        'CELL_BSF_weak'
    ])

    print('--- number of cells before cleaning up ---')
    print(get_cell_cnt(table, db_config))

    print('--- updating bsf_unified ---')
    update_bsf_uni('CELL_BSF', table, db_config, get_num_cores())

    print('--- removing constant cells ---')
    remove_constant(table, db_config)
    print('--- removing cells with redundant inputs ---')
    remove_redundant_input(table, db_config)

    print('--- updating bsf_weak_unified ---')
    update_bsf_uni('CELL_BSF_weak', table, db_config, get_num_cores())
    create_indexes(table, db_config, [
        'CELL_BSF_UNIFIED',
        'CELL_BSF_weak_UNIFIED'
    ])

    print('--- removing isomorphic cells ---')
    remove_isomorphic(table, db_config, get_num_cores())

    print('--- removing nonminimal cells ---')
    remove_nonminimal(table, db_config, get_num_cores())

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

    clean_up('NON_MINI_TEST', local_db_config, source='ONE_FIVE_LIB')
