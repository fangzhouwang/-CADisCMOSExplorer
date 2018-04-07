#!/usr/bin/env python3

import subprocess
import os


def csim(str_netlist):
    csim_path = os.path.dirname(os.path.realpath(__file__))+'/CSim'
    output = subprocess.check_output([csim_path, "-s", str_netlist])
    output = str(output)[2:-3].split(',')
    return output[0], output[1]
