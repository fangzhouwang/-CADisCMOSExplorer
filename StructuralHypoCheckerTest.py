import unittest

from Structural_hypo_checker import *
from Nonminimality_strategy import *


class HypoCheckerTestCase(unittest.TestCase):
    def test_minimal_1t(self):
        checker = StructuralHypoChecker()
        checker.set_strategy(NonminimalityStrategy())
        checker.set_netlist("M0001 GND IN001 OUT01 GND NMOS\n")
        checker.check()
        self.assertTrue(checker.is_all_bsf_same())

    def test_minimal_2t(self):
        checker = StructuralHypoChecker()
        checker.set_strategy(NonminimalityStrategy())
        checker.set_netlist("M0001 GND IN001 OUT01 GND NMOS\nM0002 VDD IN001 OUT01 VDD PMOS\n")
        checker.check()
        self.assertFalse(checker.is_all_bsf_same())

    def test_minimal_4t(self):
        checker = StructuralHypoChecker()
        checker.set_strategy(NonminimalityStrategy())
        checker.set_netlist("M0001 VDD IN001 N0001 GND NMOS\nM0002 VDD N0001 OUT01 GND NMOS\n"
                            "M0003 GND IN001 N0001 VDD PMOS\nM0004 IN002 IN001 OUT01 VDD PMOS\n")
        checker.check()
        self.assertFalse(checker.is_all_bsf_weak_diff())


if __name__ == '__main__':
    unittest.main()
