#!/usr/bin/env python2.7

import unittest
from common import alter_elements_greater_than
from reduce_bridges import Crossing
from reduce_bridges import Knot

class CommonTestCase(unittest.TestCase):
    """Tests for `common.py`."""

    def test_alter_elements_greater_than(self):
        """Are elements greater than 4 in the PD notation of a knot successfully altered?"""
        knot = Knot([Crossing(pd_code, 0) for pd_code in [[1,5,2,4],[3,6,4,7],[5,1,6,8],[7,2,8,3]]])
        altered_knot = alter_elements_greater_than(knot, 4, -2)
        correct_knot = Knot([Crossing(pd_code, 0) for pd_code in [[1,3,2,4],[3,4,4,5],[3,1,4,6],[5,2,6,3]]])

        self.assertEqual(altered_knot.pd_notation, correct_knot.pd_notation)

if __name__ == '__main__':
    unittest.main()
