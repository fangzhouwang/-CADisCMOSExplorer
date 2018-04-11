#!/usr/bin/env python3

from Circuit.CSim import *
from Circuit.Netlist import *


class StructuralHypoChecker:
    def __init__(self):
        self.netlist_ = Netlist()
        self.strategy_ = None
        self.bsf_same_cnt_ = 0
        self.bsf_diff_cnt_ = 0
        self.bsf_weak_same_cnt_ = 0
        self.bsf_weak_diff_cnt_ = 0
        self.golden_bsf_ = None
        self.golden_bsf_weak_ = None

    def set_strategy(self, strategy):
        self.strategy_ = strategy

    def set_netlist(self, str_netlist):
        self.netlist_.set_netlist(str_netlist)
        self.golden_bsf_, self.golden_bsf_weak_ = csim(str_netlist)

    def check(self):
        self.bsf_same_cnt_ = 0
        self.bsf_weak_same_cnt_ = 0
        self.bsf_diff_cnt_ = 0
        self.bsf_weak_diff_cnt_ = 0
        for str_netlist in self.strategy_.get_str_netlists(self.netlist_):
            bsf, bsf_weak = csim(str_netlist)
            if bsf == self.golden_bsf_:
                self.bsf_same_cnt_ += 1
            else:
                self.bsf_diff_cnt_ += 1
            if bsf_weak == self.golden_bsf_weak_:
                self.bsf_weak_same_cnt_ += 1
            else:
                self.bsf_weak_diff_cnt_ += 1

    def is_all_bsf_same(self):
        return self.bsf_diff_cnt_ == 0

    def is_all_bsf_weak_same(self):
        return self.bsf_weak_diff_cnt_ == 0

    def is_all_bsf_diff(self):
        return self.bsf_same_cnt_ == 0

    def is_all_bsf_weak_diff(self):
        return self.bsf_weak_same_cnt_ == 0

    def get_bsf_same_cnt(self):
        return self.bsf_same_cnt_

    def get_bsf_weak_same_cnt(self):
        return self.bsf_weak_same_cnt_

    def print_report_summary(self):
        print('--- summary ---')
        if self.bsf_diff_cnt_ == 0:
            # print(f'{Fore.GREEN}[OK]{Style.RESET_ALL} bsf all the same')
            print('[OK] bsf all the same')
        else:
            print('[--] bsf not the same')
        if self.bsf_weak_diff_cnt_ == 0:
            print('[OK] weak bsf all the same')
        else:
            print('[--] weak bsf not the same')

        print('--- detail ---')
        print(f'Total instances: {self.bsf_same_cnt_+self.bsf_diff_cnt_}')
        print(f'Same bsf instances: {self.bsf_same_cnt_}')
        print(f'Diff bsf instances: {self.bsf_diff_cnt_}')
        print(f'Same weak instances: {self.bsf_weak_same_cnt_}')
        print(f'Diff weak instances: {self.bsf_weak_diff_cnt_}')
        print('--- end ---')
