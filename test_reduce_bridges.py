#!/usr/bin/env python2.7

import itertools, unittest
from reduce_bridges import *

# Tests for Crossing methods.
class AlterElementsGreaterThanTestCase(unittest.TestCase):
  def testPositiveAddend(self):
    crossing = Crossing([1,2,3,4], 0)
    crossing.alter_elements_greater_than(2, 1)
    self.assertEqual(crossing.pd_code, [1,2,4,5])

  def testNegativeAddend(self):
    crossing = Crossing([1,2,3,4], 0)
    crossing.alter_elements_greater_than(2, -1)
    self.assertEqual(crossing, Crossing([1,2,2,3],0))

class HasDuplicateValueTestCase(unittest.TestCase):
  def testHasDuplicateValue(self):
    pd_codes = itertools.permutations([1, 2, 3, 3])
    for pd_code in pd_codes:
      crossing = Crossing(pd_code, 0)
      self.assertEqual(crossing.has_duplicate_value(), 3)

  def testHasTwoDuplicateValues(self):
    pd_codes = itertools.permutations([1, 1, 2, 2])
    for pd_code in pd_codes:
      crossing = Crossing(pd_code, 0)
      self.assertEqual(crossing.has_duplicate_value(), 1)

  def testNoDuplicateValue(self):
    pd_codes = itertools.permutations([1, 2, 3, 4])
    for pd_code in pd_codes:
      crossing = Crossing(pd_code, 0)
      self.assertEqual(crossing.has_duplicate_value(), False)

if __name__ == '__main__':
  unittest.main()
