import unittest
from ULM_cell import *


class ULMTestCase(unittest.TestCase):
    def test_construct_from_template_inv(self):
        ulm_tester = ULMCell()
        results = set()
        for netlist in ulm_tester.construct_cells_from_ulm_template(ulm_tester.templates[0]):
            results.add(netlist)
        self.assertEqual(25, len(results))

    def test_construct_from_template_nand(self):
        ulm_tester = ULMCell()
        results = set()
        for netlist in ulm_tester.construct_cells_from_ulm_template(ulm_tester.templates[1]):
            results.add(netlist)
        self.assertEqual(25, len(results))

    def test_construct_ulm_cells(self):
        ulm_tester = ULMCell()
        results = set()
        for netlist in ulm_tester.construct_ulm_cells():
            results.add(netlist)
        self.assertEqual(25*3, len(results))

    def test_construct_inv_polarity_from_template_inv(self):
        ulm_tester = ULMCell()
        results = set()
        for netlist in ulm_tester.construct_ulm_inv_polarity_cells_from_strnetlist(
            "M0001 OUT01 IN001 N0001 GND NMOS\n"
            "M0002 GND IN002 N0001 GND NMOS\n"
            "M0003 VDD IN001 OUT01 VDD PMOS\n"
            "M0004 VDD IN002 OUT01 VDD PMOS\n"
        ):
            results.add(netlist)
        self.assertCountEqual(
            [
                "M0001 GND IN002 N0001 GND NMOS\n"
                "M0002 VDD IN001 OUT01 GND NMOS\n"
                "M0003 VDD IN002 OUT01 VDD PMOS\n"
                "M0004 OUT01 IN001 N0001 VDD PMOS\n"
                ,
                "M0001 OUT01 IN001 N0001 GND NMOS\n"
                "M0002 VDD IN002 OUT01 GND NMOS\n"
                "M0003 VDD IN001 OUT01 VDD PMOS\n"
                "M0004 GND IN002 N0001 VDD PMOS\n"
            ], results
        )


if __name__ == '__main__':
    unittest.main()
