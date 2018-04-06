#!/usr/bin/env python3
__version__ = '1.0.0'

from ArkLibPy.ArkDBMySQL import ArkDBMySQL
import itertools
import math
from tqdm import tqdm
import sys


def is_power2(num):
    return num != 0 and ((num & (num - 1)) == 0)


def int_to_bin_str(num, length):
    format_str = "{:0" + str(length) + "b}"
    return format_str.format(num)


def convert_idx_for_title(idx, title):
    idx_bin = int_to_bin_str(idx, len(title))
    ret = ''
    for i in range(len(title)):
        ret += idx_bin[title[i]]
    return int(ret, 2)


def convert_bsf_for_title(bsf, title):
    ret = ''
    for new_idx in range(pow(2, len(title))):
        base_idx = convert_idx_for_title(new_idx, title)   # convert the idx of new title to idx of base title
        ret += bsf[base_idx]
    return ret


def gen_equ_bsf(bsf):
    if not is_power2(len(bsf)):
        raise ValueError('length of a bsf must be power of 2')
    if len(bsf) == 1:
        return bsf, list(bsf)

    input_list = list(range(int(math.log(len(bsf), 2))))
    equ_bsf_set = set()
    for title in itertools.permutations(input_list):
        new_bsf = convert_bsf_for_title(bsf, title)
        equ_bsf_set.add(new_bsf)
    equ_bsf_list = list(equ_bsf_set)
    equ_bsf_list.sort()
    return equ_bsf_list[0], equ_bsf_list


def get_last_input_degen(bsf):
    if len(bsf) == 1:
        return bsf
    for i in range(1, len(bsf), 2):
        if bsf[i-1] != bsf[i]:
            return bsf
    return bsf[1::2]    # return every other item in bsf


def get_degen_bsf(bsf):
    uni_bsf, bsf_list = gen_equ_bsf(bsf)
    for equ_bsf in bsf_list:
        degen_bsf = get_last_input_degen(equ_bsf)
        if degen_bsf != equ_bsf:
            further_degen = get_degen_bsf(degen_bsf)
            if further_degen == degen_bsf:
                return degen_bsf
            else:
                return further_degen
    return bsf


def gen_all_bsf(input_cnt, symbol_options):
    bsf_list = list()
    for bsf_tupple in tqdm(itertools.product(symbol_options, repeat=pow(2, input_cnt)), desc='Gen all BSF'):
        bsf = ''
        for i in bsf_tupple:
            bsf += i
        bsf_list.append(bsf)
    return bsf_list


def get_uni_dict(input_cnt, symbol_options):
    uni_bsf_dict = dict()

    for bsf in tqdm(gen_all_bsf(input_cnt, symbol_options), desc='Get Uni Dict'):
        uni_bsf, bsf_list = gen_equ_bsf(bsf)
        uni_bsf = get_degen_bsf(uni_bsf)
        if uni_bsf not in uni_bsf_dict:
            uni_bsf_dict[uni_bsf] = set()
        uni_bsf_dict[uni_bsf] = uni_bsf_dict[uni_bsf].union(bsf_list)

    return uni_bsf_dict


def create_bsf_table(input_cnt, db_config_file):
    db = ArkDBMySQL(db_config_file=db_config_file)

    # db.run_sql(f'DROP TABLE IF EXISTS BSF_LIB')
    create_table_sql = 'CREATE TABLE IF NOT EXISTS `CADisCMOS`.`BSF_LIB` (\
        `BSF` VARCHAR(256) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,\
        `BSF_UNI` VARCHAR(256) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL NOT NULL,\
        PRIMARY KEY (`BSF`))\
        ENGINE = InnoDB'

    # create the BSF_LIB table if it does not exist
    db.run_sql(create_table_sql)
    db.set_table('BSF_LIB')

    uni_bsf_dict = get_uni_dict(input_cnt, ['0', '1', 'o', 'i', 'Z', 'X', 'R', 'r'])

    for key in tqdm(uni_bsf_dict.keys(), desc='Insert into DB'):
        rec = dict()
        rec['BSF_UNI'] = key
        for bsf in uni_bsf_dict[key]:
            rec['BSF'] = bsf
            db.insert_nocommit(rec)
    db.commit()


def update_bsf_uni_for_table(bsf_col, target_lib, db_config_file):
    db = ArkDBMySQL(db_config_file=db_config_file)
    query = 'SELECT * FROM BSF_LIB'
    uni_bsf_arr = db.run_query_get_all_row(query)

    for row in tqdm(uni_bsf_arr, desc='Update BSF_UNI'):
        res = db.run_query_get_all_row(f'SELECT idCELL FROM {target_lib} WHERE {bsf_col} = %s',
                                       [row['BSF'].decode("utf-8")])
        id_list = list()
        for record in res:
            id_list.append(record['idCELL'])
        if len(id_list) == 0:
            continue
        id_list_str = ', '.join(map(lambda s: '{}'.format(s), id_list))
        db.run_sql_nocommit(f'UPDATE {target_lib} SET {bsf_col}_UNIFIED = %s WHERE idCELL in ({id_list_str})',
                            [row['BSF_UNI'].decode("utf-8")])
    db.commit()


if __name__ == '__main__':
    if len(sys.argv != 4):
        print('item, table, db_config')
        exit(1)
    item = sys.argv[1]
    table = sys.argv[2]
    db_config = sys.argv[3]
    # db_config = '/home/fangzhou/.db_configs/db_config_local_cadis.txt'
    update_bsf_uni_for_table(item, table, db_config)
