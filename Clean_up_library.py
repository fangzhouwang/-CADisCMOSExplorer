#!/usr/bin/env python3

from Eliminate_structural_iso import *


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


def remove_iso_cells(table, db_config):
    elm = ISOEliminator(db_config, table)
    elm.eliminate_iso()

    print(get_cell_cnt(table, db_config))


def clean_up(table, db_config, source='RAW_DATA_LIB'):
    print(f'--- duplicating {source} as {table}---')
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

    print('--- updating bsf_unified, this may take about 3 hours ---')
    # setup UNI bsf - about 3 hours for 1~5-t cells
    # update_bsf_uni_for_table('CELL_BSF', table, db_config)

    # print('---  ---')
    print('--- removing constant cells ---')
    remove_constant(table, db_config)
    print('--- removing cells with redundant inputs ---')
    remove_redundant_input(table, db_config)

    # update_bsf_uni_for_table('CELL_BSF_weak', table, db_config)
    create_indexes(table, db_config, [
        'CELL_BSF_UNIFIED',
        'CELL_BSF_weak_UNIFIED'
    ])

    # print('--- removing isomorphic cells ---')
    # remove_iso_cells(table, db_config)


if __name__ == '__main__':
    # local_db_config = '/Users/Ark/.db_configs/db_config_local_cadis.txt'
    # local_db_config = '/home/fangzhou/.db_configs/db_config_local_cadis.txt'
    # local_db_config = '/Users/Ark/.db_configs/db_config_dfx_cadis.txt'

    local_db_config = '/Users/Ark/.db_configs/db_config_dfx_cadis.txt'
    # clean_up('NO_ISO_LIB', db_config)
    # clean_up('ONE_FIVE_LIB', db_config)
    local_db = ArkDBMySQL(db_config_file=local_db_config)
    local_db.set_table('ONE_FIVE_LIB')

    print(local_db.get_table_disk_size())
    local_db.optimize()
    print(local_db.get_table_disk_size())
