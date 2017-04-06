#!/usr/bin/env python2.7

import unittest
from rm1 import has_duplicate_value
from rm1 import check_rm1
from reduce_bridges import Crossing
from reduce_bridges import Knot

class Rm1TestCase(unittest.TestCase):
    def test_simplify_rm1(self):

    >>> simplify_rm1([1, 2, 3], [[1, 5, 2, 4], [3, 3, 4, 2], [6, 6, 7, 5], [8, 8, 1, 7]])
    [[1, 3, 2, 2]]
    >>> simplify_rm1([0], [[1, 1, 2, 2]])
    []


if __name__ == '__main__':
    unittest.main()
