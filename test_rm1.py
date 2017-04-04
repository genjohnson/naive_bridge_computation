#!/usr/bin/env python2.7

import unittest
from rm1 import has_duplicate_value
from rm1 import check_rm1
from reduce_bridges import Crossing
from reduce_bridges import Knot

class Rm1TestCase(unittest.TestCase):
    """Tests for `rm1.py`."""

    def test_has_duplicate_value(self):
        """Is [1,2,3,3] successfully determined to contain a duplicate value?"""
        self.assertNotEqual(has_duplicate_value([1,2,3,3]), False)
        """Is [1,2,3,4] successfully determined to not contain a duplicate value?"""
        self.assertFalse(has_duplicate_value([1,2,3,4]))

    def test_check_rm1(self):
      """Is a knot successfully determined to contain a twisted crossing?"""
      knot = Knot([Crossing(pd_code, 0) for pd_code in [[1,2,2,3]]])
      self.assertNotEqual(check_rm1(knot), False)
      """Is a knot successfully determined to contain no twisted crossings?"""
      knot = Knot([Crossing(pd_code, 0) for pd_code in [[1,5,2,4],[3,1,4,6],[5,3,6,2]]])
      self.assertFalse(check_rm1(knot))

    def test_simplify_rm1(self):

    >>> simplify_rm1([1, 2, 3], [[1, 5, 2, 4], [3, 3, 4, 2], [6, 6, 7, 5], [8, 8, 1, 7]])
    [[1, 3, 2, 2]]
    >>> simplify_rm1([0], [[1, 1, 2, 2]])
    []


if __name__ == '__main__':
    unittest.main()
