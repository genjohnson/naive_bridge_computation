#!/usr/bin/env python2.7

import itertools, unittest
from reduce_bridges import *

# Tests for Crossing methods.
class AlterElementsGreaterThanTestCase(unittest.TestCase):
    def testPositiveAddend(self):
        crossing = Crossing([1,2,3,4], 0)
        crossing.alter_elements_greater_than(2, 1, 3)
        self.assertEqual(crossing.pd_code, [1,2,1,2])

    def testNegativeAddend(self):
        crossing = Crossing([1,2,3,4], 0)
        crossing.alter_elements_greater_than(2, -1, 2)
        self.assertEqual(crossing, Crossing([1,2,2,1],0))

class HasDuplicateValueTestCase(unittest.TestCase):
    def testHasDuplicateValue(self):
        pd_codes = itertools.permutations([1, 2, 3, 3])
        for pd_code in pd_codes:
            crossing = Crossing(pd_code)
            self.assertEqual(crossing.has_duplicate_value(), 3)

    def testHasTwoDuplicateValues(self):
        pd_codes = itertools.permutations([1, 1, 2, 2])
        for pd_code in pd_codes:
            crossing = Crossing(pd_code)
            self.assertEqual(crossing.has_duplicate_value(), 1)

    def testNoDuplicateValue(self):
        pd_codes = itertools.permutations([1, 2, 3, 4])
        for pd_code in pd_codes:
            crossing = Crossing(pd_code)
            self.assertEqual(crossing.has_duplicate_value(), False)

# Tests for Knot methods
class HasRm1TestCase(unittest.TestCase):
    def testHasRm1(self):
        knot = create_knot_from_pd_code([[1,5,2,4],[3,3,4,2],[6,6,7,5],[8,8,1,7]])
        self.assertEqual(knot.has_rm1(), [1,2,3])

    def testDoesNotHaveRm1(self):
        knot = create_knot_from_pd_code([[1,5,2,4],[3,1,4,6],[5,3,6,2]])
        self.assertEqual(knot.has_rm1(), False)

class HasRm2TestCase(unittest.TestCase):
    def testHasRm2(self):
        # Consecutive tuples form an arc of type 1.
        knot = create_knot_from_pd_code([[1,2,3,4],[1,3,2,4],[5,6,7,8]])
        self.assertEqual(knot.has_rm2(), ([0,1], [2,3]))

        # The first and last tuple form an arc of type 1.
        knot = create_knot_from_pd_code([[1,3,2,4],[5,6,7,8],[1,2,3,4]])
        self.assertEqual(knot.has_rm2(), ([2,0], [2,3]))

        # The first and last tuple form an arc of type 2.
        knot = create_knot_from_pd_code([[1,5,2,4],[2,5,3,6],[6,3,1,4]])
        self.assertEqual(knot.has_rm2(), ([2,0], [1,4]))

        # Consecutive tuples form an arc of type 2.
        knot = create_knot_from_pd_code([[1,4,2,5],[5,2,6,3],[6,4,1,3]])
        self.assertEqual(knot.has_rm2(), ([1,2], [6,3]))

class DeleteCrossingsTestCase(unittest.TestCase):
    def testDeleteCrossings(self):
        knot = create_knot_from_pd_code([[1,5,2,4],[3,6,4,7],[5,1,6,8],[7,2,8,3]])
        knot.delete_crossings([2,1,3])
        answer = create_knot_from_pd_code([[1,5,2,4]])
        self.assertEqual(knot, answer)

class DesignateBridgeTestCase(unittest.TestCase):
    def testDesignateBridge(self):
        knot = create_knot_from_pd_code([[1,15,2,14],[5,17,6,16],[6,12,7,11],[9,5,10,4],[10,16,11,15],[12,8,13,7],[13,3,14,2],[17,9,18,8],[18,4,1,3]])
        knot.designate_bridge(knot.crossings[0])
        answer = Knot([Crossing(x[0],x[1]) for x in [[[1, 15, 2, 14], 0],[[5, 17, 6, 16], 0],[[6, 12, 7, 11], None],[[9, 5, 10, 4], None],[[10, 16, 11, 15], 0],[[12, 8, 13, 7], None],[[13, 3, 14, 2], None],[[17, 9, 18, 8], None],[[18, 4, 1, 3], None]]])
        self.assertEqual(knot, answer)

class SimplifyRm1TestCase(unittest.TestCase):
    def testSimplifyRm1(self):
        knot = create_knot_from_pd_code([[1,5,2,4],[3,3,4,2],[6,6,7,5],[8,8,1,7]])
        knot.simplify_rm1([1,2,3])
        answer = create_knot_from_pd_code([[1,3,2,2]])
        self.assertEqual(knot, answer)
    
class SimplifyRm1RecursivelyTestCase(unittest.TestCase):
    def testSimplifyRm1Recursively(self):
        knot = create_knot_from_pd_code([[1,5,2,4],[3,3,4,2],[7,10,8,1],[8,6,9,5],[9,6,10,7]])
        knot.simplify_rm1_recursively()
        answer = create_knot_from_pd_code([[3,6,4,1],[4,2,5,1],[5,2,6,3]])
        self.assertEqual(knot, answer)

class SimplifyRm1Rm2RecursivelyTestCase(unittest.TestCase):
    def testSimplifyRm1Rm2Recursively(self):
        knot = create_knot_from_pd_code([[1,7,2,6],[2,9,3,10],[5,1,6,10],[7,5,8,4],[8,3,9,4]])
        knot.simplify_rm1_rm2_recursively()
        answer = Knot([])
        self.assertEqual(knot, answer)

class SimplifyRm2TestCase(unittest.TestCase):
    def testSimplifyRm2(self):
        knot = create_knot_from_pd_code([[1,7,2,6],[2,9,3,10],[5,1,6,10],[7,5,8,4],[8,3,9,4]])
        knot.simplify_rm2([3,4], [8,4])
        answer = create_knot_from_pd_code([[1, 5, 2, 4],[2, 5, 3, 6],[3, 1, 4, 6]])
        self.assertEqual(knot, answer)

        # One of the segments to be removed is 1.
        knot = create_knot_from_pd_code([[2,12,3,11],[3,10,4,11],[4,5,5,6],[6,1,7,2],[7,1,8,14],[8,13,9,14],[9,13,10,12]])
        knot.simplify_rm2([3,4], [7,1])
        answer = create_knot_from_pd_code([[1,9,2,8],[2,7,3,8],[3,4,4,5],[5,10,6,1],[6,10,7,9]], 'answer')
        self.assertEqual(knot, answer)

class SimplifyRm2RecursivelyTestCase(unittest.TestCase):
    def testSimplifyRm2Recursively(self):
        knot = create_knot_from_pd_code([[1,7,2,6],[2,9,3,10],[5,1,6,10],[7,5,8,4],[8,3,9,4]])
        knot.simplify_rm2_recursively()
        answer = create_knot_from_pd_code([[1,1,2,2]])
        self.assertEqual(knot, answer)

if __name__ == '__main__':
    unittest.main()
