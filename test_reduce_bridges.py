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

# Tests for Knot methods
class HasRm1TestCase(unittest.TestCase):
  def testHasRm1(self):
    knot = Knot([Crossing(pd_code, 0) for pd_code in [[1,5,2,4],[3,3,4,2],[6,6,7,5],[8,8,1,7]]])
    self.assertEqual(knot.has_rm1(), [1,2,3])

  def testDoesNotHaveRm1(self):
    knot = Knot([Crossing(pd_code, 0) for pd_code in [[1,5,2,4],[3,1,4,6],[5,3,6,2]]])
    self.assertEqual(knot.has_rm1(), False)

if __name__ == '__main__':
  unittest.main()
