#!/usr/bin/env python3

import subprocess
import sys
import os


def csim(str_netlist):
    if sys.platform == 'linux':
        csim_path = os.path.dirname(os.path.realpath(__file__))+'/CSim_linux'
    elif sys.platform == 'darwin':
        csim_path = os.path.dirname(os.path.realpath(__file__))+'/CSim_mac'
    else:
        csim_path = 'ERROR'
        print(f'Error: CSim is not compiled for {sys.platform} yet.')
        exit(1)

    output = subprocess.check_output([csim_path, f'-netlist={str_netlist}'])
    output = str(output)[2:-3].split(',')
    return output[0], output[1]
