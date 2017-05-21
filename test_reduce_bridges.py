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

class AlterForDrag(unittest.TestCase):
    def testAlterForDrag(self):
        crossing = Crossing([12,2,13,1])
        crossing.alter_for_drag([3,8])
        self.assertEqual(crossing, Crossing([16,2,17,1]))

    def testAlterForDragTwo(self):
        crossing = Crossing([16,10,1,9])
        crossing.alter_for_drag([3,8])
        self.assertEqual(crossing, Crossing([20,14,1,13]))

    def testAlterForDragThree(self):
        crossing = Crossing([5,11,6,10])
        crossing.alter_for_drag([3,8])
        self.assertEqual(crossing, Crossing([7,15,8,14]))

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
        self.assertEqual(knot.has_rm1(), [1])

    def testDoesNotHaveRm1(self):
        knot = create_knot_from_pd_code([[1,5,2,4],[3,1,4,6],[5,3,6,2]])
        self.assertEqual(knot.has_rm1(), False)

class HasRm2TestCase(unittest.TestCase):
    def testHasRm2(self):
        # The first and last tuple form an arc of type 2.
        knot = create_knot_from_pd_code([[2,5,3,6],[4,3,5,4],[7,1,8,8],[1,7,2,6]])
        self.assertEqual(knot.has_rm2(), ([3,0], [[2, -2], [6, -2]]))

        # Consecutive tuples form an arc of type 2.
        knot = create_knot_from_pd_code([[1,7,2,6],[2,5,3,6],[4,3,5,4],[7,1,8,8]])
        self.assertEqual(knot.has_rm2(), ([0,1], [[2, -2], [6, -2]]))

        # Consecutive tuples form an arc of type 3.
        knot = create_knot_from_pd_code([[1,15,2,14],[3,10,4,11],[5,13,6,12],[6,13,7,14],[16,24,17,23],[17,3,18,2],[18,11,19,12],[19,4,20,5],[20,25,21,26],[21,9,22,8],[22,16,23,15],[24,9,25,10],[26,8,1,7]])
        self.assertEqual(knot.has_rm2(), ([2,3], [[13,-2], [6, -2]]))

        # The first and last tuples form an arc of type 3.
        knot = create_knot_from_pd_code([[6,13,7,14],[16,24,17,23],[17,3,18,2],[18,11,19,12],[19,4,20,5],[20,25,21,26],[21,9,22,8],[22,16,23,15],[24,9,25,10],[26,8,1,7],[1,15,2,14],[3,10,4,11],[5,13,6,12]])
        self.assertEqual(knot.has_rm2(), ([12,0], [[13,-2], [6, -2]]))

        # Two arcs share a crossing.
        knot = create_knot_from_pd_code([[1,4,2,5],[2,6,3,5],[3,6,4,1]], 'two arcs')
        self.assertEqual(knot.has_rm2(), ([0,1], [[2,-2], [5,-2]]))

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

class DragCrossingUnderBridgeTestCase(unittest.TestCase):
    def testdrag_crossing_under_bridge(self):
        knot = create_knot_from_pd_code([[1,5,2,4],[3,11,4,10],[5,8,6,9],[7,12,8,1],[9,3,10,2],[11,6,12,7]])
        knot.designate_bridge(knot.crossings[0])
        knot.designate_additional_bridge()
        drag_info = knot.find_crossing_to_drag()
        knot.drag_crossing_under_bridge(drag_info[2], drag_info[3])
        answer = Knot([Crossing(x[0], x[1]) for x in [[[16,6,1,5],0], [[3,15,4,14], None], [[7,12,8,13], 1], [[9,5,10,4], 0], [[10,1,11,2], 0], [[11,6,12,7], 0], [[13,3,14,2], None], [[15,8,16,9], None]]])
        self.assertEqual(knot, answer)

class SimplifyRm1TestCase(unittest.TestCase):
    def testSimplifyRm1(self):
        knot = create_knot_from_pd_code([[1,5,2,4],[3,3,4,2],[6,6,7,5],[8,8,1,7]])
        knot.simplify_rm1([1])
        answer = create_knot_from_pd_code([[1,3,2,2],[4,4,5,3],[6,6,1,5]])
        self.assertEqual(knot, answer)

class SimplifyRm1RecursivelyTestCase(unittest.TestCase):
    def testSimplifyRm1Recursively(self):
        knot = create_knot_from_pd_code([[1,5,2,4],[3,3,4,2],[7,10,8,1],[8,6,9,5],[9,6,10,7]])
        knot.simplify_rm1_recursively()
        answer = create_knot_from_pd_code([[3,6,4,1],[4,2,5,1],[5,2,6,3]])
        self.assertEqual(knot, answer)

class SimplifyRm1Rm2RecursivelyTestCase(unittest.TestCase):
    def testSimplifyRm1Rm2Recursively(self):
        knot = create_knot_from_pd_code([[1,7,2,6],[2,5,3,6],[4,3,5,4],[7,1,8,8]])
        knot.simplify_rm1_rm2_recursively()
        answer = Knot([])
        self.assertEqual(knot, answer)

class SimplifyRm2TestCase(unittest.TestCase):
    def testSimplifyRm2(self):
        # One arc to remove and none of the semgnets to be removed is 1.
        knot = create_knot_from_pd_code([[1,7,2,6],[2,9,3,10],[5,1,6,10],[7,5,8,4],[8,3,9,4]])
        knot.simplify_rm2([3,4], [[8,-2], [4, -2]])
        answer = create_knot_from_pd_code([[1,5,2,4],[2,5,3,6],[3,1,4,6]])
        self.assertEqual(knot, answer)

        # One arc to remove and one of the segments to be removed is 1.
        knot = create_knot_from_pd_code([[2,12,3,11],[3,10,4,11],[4,5,5,6],[6,1,7,2],[7,1,8,14],[8,13,9,14],[9,13,10,12]])
        knot.simplify_rm2([3,4], [[7, -2],[1, -1]])
        answer = create_knot_from_pd_code([[1,9,2,8],[2,7,3,8],[3,4,4,5],[5,10,6,1],[6,10,7,9]])
        self.assertEqual(knot, answer)

        # Two arcs share a crossing.
        knot = create_knot_from_pd_code([[1,4,2,5],[2,6,3,5],[3,6,4,1]], 'two arcs')
        move = knot.has_rm2()
        knot.simplify_rm2(move[0], move[1])
        answer = create_knot_from_pd_code([[1,2,2,1]])
        self.assertEqual(knot, answer)

class SimplifyRm2RecursivelyTestCase(unittest.TestCase):
    def testSimplifyRm2Recursively(self):
        knot = create_knot_from_pd_code([[1,13,2,12],[2,21,3,22],[3,14,4,15],[4,18,5,17],[5,25,6,24],[6,12,7,11],[7,22,8,23],[8,15,9,16],[9,17,10,16],[10,24,11,23],[18,26,19,25],[19,26,20,1],[20,14,21,13]])
        knot.simplify_rm2_recursively()
        answer = create_knot_from_pd_code([[1,5,2,4],[2,4,3,3],[6,6,1,5]])
        self.assertEqual(knot, answer)

if __name__ == '__main__':
    unittest.main()
