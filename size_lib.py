#!/usr/bin/env python3


__version__ = '1.0.0'

from ArkLibPy.ArkDBMySQL import ArkDBMySQL
import itertools
import sys


def gen_size_desc(tx_cnt, sizing_options):
    return itertools.product(sizing_options, repeat=tx_cnt)


def gen_sizes(tx_cnt, sizing_options):
    for size_desc in gen_size_desc(tx_cnt, sizing_options):
        str_size_desc = ''
        area = 0
        for size in size_desc:
            str_size_desc += str(size)
            area += int(size)
        yield str_size_desc, area


if __name__ == '__main__':
    db_config = sys.argv[1]
    db = ArkDBMySQL(db_config_file=db_config)

    create_table_sql = 'CREATE TABLE IF NOT EXISTS `CADisCMOS`.`SIZE_LIB` (\
        `idSIZE_LIB` INT NOT NULL AUTO_INCREMENT,\
        `SIZE_DESC` VARCHAR(45) NOT NULL,\
        `TX_CNT` INT NOT NULL,\
        `SIZE_AREA` INT NULL,\
        PRIMARY KEY (`idSIZE_LIB`))\
        ENGINE = InnoDB'

    # create the SIZE_LIB table if it does not exist
    db.run_sql(create_table_sql)
    db.set_table('SIZE_LIB')

    for i in range(1, 8):
        rec = {'TX_CNT': i}
        for rec['SIZE_DESC'], rec['SIZE_AREA'] in gen_sizes(rec['TX_CNT'], [1, 2, 3, 4]):
            db.insert_nocommit(rec)
        db.commit()
