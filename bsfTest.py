#!/usr/bin/env python3

import unittest
from bsf import *


class BSFTestCase(unittest.TestCase):
    """
    def test_invalid_bsf(self):
        self.assertRaises(ValueError, gen_equ_bsf('0'))
    """

    def test_gen_equ_bsf_const(self):
        uni_bsf, equ_bsf_list = gen_equ_bsf('0')
        self.assertEqual(uni_bsf, '0')
        self.assertCountEqual(equ_bsf_list, ['0'])

    def test_gen_equ_bsf(self):
        uni_bsf, equ_bsf_list = gen_equ_bsf('10011010')
        self.assertEqual(uni_bsf, '10011010')
        self.assertCountEqual(equ_bsf_list, ['10011010', '10011100', '10100110', '10110100', '11000110', '11010010'])

    def test_gen_equ_bsf_with_dup(self):
        uni_bsf, equ_bsf_list = gen_equ_bsf('10011110')
        self.assertEqual(uni_bsf, '10011110')
        self.assertCountEqual(equ_bsf_list, ['10011110', '10110110', '11010110'])

    def test_gen_equ_bsf_degen(self):
        uni_bsf, equ_bsf_list = gen_equ_bsf('10011110')
        self.assertEqual(uni_bsf, '10011110')
        self.assertCountEqual(equ_bsf_list, ['10011110', '10110110', '11010110'])

    def test_convert_idx(self):
        # 010 --> 001
        # 2 --> 1
        idx = convert_idx_for_title(2, [2, 0, 1])
        self.assertEqual(idx, 1)

        # 0100 --> 0100
        # 4 --> 4
        idx = convert_idx_for_title(4, [0, 1, 2, 3])
        self.assertEqual(idx, 4)

    def test_convert_bsf(self):
        # IN1 IN2 --> IN2 IN1
        # 0100 --> 0010
        bsf = convert_bsf_for_title('0100', [1, 0])
        self.assertEqual(bsf, '0010')

    def test_last_input_degen(self):
        self.assertEqual(get_last_input_degen('0'), '0')
        self.assertEqual(get_last_input_degen('0011'), '01')
        self.assertEqual(get_last_input_degen('00111100'), '0110')
        self.assertEqual(get_last_input_degen('00000011'), '0001')
        self.assertEqual(get_last_input_degen('0101'), '0101')   # degen but not last input, hence False
        self.assertEqual(get_last_input_degen('0110'), '0110')
        self.assertEqual(get_last_input_degen('01'), '01')

    def test_degen_bsf(self):
        self.assertEqual(get_degen_bsf('0011'), '01')
        self.assertEqual(get_degen_bsf('0101'), '01')
        self.assertEqual(get_degen_bsf('00001111'), '01')
        self.assertEqual(get_degen_bsf('00000101'), '0001')
        self.assertEqual(get_degen_bsf('00000000'), '0')

        self.assertEqual(get_degen_bsf('0110'), '0110')
        self.assertEqual(get_degen_bsf('01'), '01')

    def test_gen_all_bsf(self):
        self.assertCountEqual(list(gen_all_bsf(0, ['0', '1'])), ['1', '0'])
        self.assertCountEqual(list(gen_all_bsf(1, ['0', '1'])), ['01', '10', '00', '11'])
        self.assertCountEqual(list(gen_all_bsf(2, ['0', '1'])), ['0000', '0001', '0010', '0011',
                                                                 '0100', '0101', '0110', '0111',
                                                                 '1000', '1001', '1010', '1011',
                                                                 '1100', '1101', '1110', '1111'])


if __name__ == '__main__':
    unittest.main()
