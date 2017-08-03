#!/usr/bin/env python2.7

import itertools, unittest
from reduce_bridges import *

logging.basicConfig(filename='tests.log', filemode='w', format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

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
    # def testDesignateNonAdjacentBridge(self):
    #     knot = create_knot_from_pd_code([[1,8,2,9],[3,11,4,10],[5,1,6,12],[7,2,8,3],[9,7,10,6],[11,5,12,4]])
    #     knot.designate_bridge(knot.crossings[0])
    #     knot.designate_additional_bridge()
    #     answer = Knot([Crossing(x[0],x[1]) for x in [[[1,8,2,9],0],[[3,11,4,10],None],[[5,1,6,12],None],[[7,2,8,3],1],[[9,7,10,6],None],[[11,5,12,4],None]]])
    #     self.assertEqual(knot, answer)

class DragCrossingUnderBridgeTestCase(unittest.TestCase):
    # Dragging case b=g, a>y, y==f
    def testDragCrossingUnderBridge(self):
        knot = create_knot_from_pd_code([[1,5,2,4],[3,11,4,10],[5,8,6,9],[7,12,8,1],[9,3,10,2],[11,6,12,7]], bridges = {0:[5,4],1:[8,9]})
        knot.drag_crossing_under_bridge(knot.crossings[5], 6)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[1,5,2,4],0], [[3,13,4,12], None], [[6,9,7,10], 1], [[7,16,8,1], None], [[11,3,12,2], None], [[13,11,14,10], 1], [[14,5,15,6], 0], [[15,8,16,9], 1]]])
        self.assertEqual(knot, answer)

    # Dragging case b=g, a>y, y==f
    def testDragCrossingUnderBridge_1(self):
        knot = create_knot_from_pd_code([[2,5,3,6],[4,1,5,2],[6,3,1,4]], bridges = {0:[5,6],1:[3,4]})
        knot.drag_crossing_under_bridge(knot.crossings[1], 1)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[2,9,3,10],0],[[6,6,7,5],1],[[7,10,8,1],0],[[8,3,9,4],1],[[1,4,2,5],1]]])
        self.assertEqual(knot, answer)

    # Dragging case b=g, a<y, y==h
    def testDragCrossingUnderBridge_2(self):
        knot = create_knot_from_pd_code([[1,9,2,8],[3,7,4,6],[5,10,6,11],[7,3,8,2],[9,1,10,12],[11,4,12,5]], bridges = {0:[9,8],1:[1,12]})
        knot.drag_crossing_under_bridge(knot.crossings[2], 10)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[1,11,2,10],0],[[3,9,4,8],None],[[5,14,6,15],1],[[6,11,7,12],0],[[7,1,8,16],1],[[9,3,10,2],None],[[12,16,13,15],1],[[13,4,14,5],None]]])
        self.assertEqual(knot, answer)

    # Dragging case d=g, a<y, y==h
    def testDragCrossingUnderBridge_3(self):
        knot = create_knot_from_pd_code([[1,11,2,10],[3,9,4,8],[5,14,6,15],[6,11,7,12],[7,1,8,16],[9,3,10,2],[12,16,13,15],[13,4,14,5]], bridges = {0:[11,10],1:[14,15]})
        knot.drag_crossing_under_bridge(knot.crossings[5], 2)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[2,14,3,13],0],[[3,9,4,8],None],[[5,18,6,19],1],[[6,15,7,16],0],[[7,1,8,20],1],[[9,14,10,15],0],[[10,2,11,1],1],[[11,13,12,12],0],[[16,20,17,19],1],[[17,4,18,5],None]]])
        self.assertEqual(knot, answer)

    # Dragging case d=g, a<y, y==f
    def testDragCrossingUnderBridge_4(self):
        knot = create_knot_from_pd_code([[1,4,2,5],[3,7,4,6],[5,8,6,1],[7,3,8,2]], bridges = {0:[4,5],1:[8,1]})
        knot.drag_crossing_under_bridge(knot.crossings[1], 6)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[1,6,2,7],0],[[3,11,4,10],1],[[4,8,5,7],0],[[5,12,6,1],1],[[8,11,9,12],1],[[9,3,10,2],None]]])
        self.assertEqual(knot, answer)

    # Dragging case d=g, a>y, y==f
    def testDragCrossingUnderBridge_5(self):
        knot = create_knot_from_pd_code([[1,6,2,7],[3,11,4,10],[4,8,5,7],[5,12,6,1],[8,11,9,12],[9,3,10,2]], bridges = {0:[6,7],1:[12,1]})
        knot.drag_crossing_under_bridge(knot.crossings[5], 2)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[2,7,3,8],0],[[3,15,4,14],1],[[4,10,5,9],0],[[5,16,6,1],1],[[10,15,11,16],1],[[11,7,12,6],0],[[12,2,13,1],1],[[13,8,14,9],0]]])
        self.assertEqual(knot, answer)

    # Dragging case b=e, a<y, y==h
    def testDragCrossingUnderBridge_6(self):
        knot = create_knot_from_pd_code([[1,6,2,7],[3,11,4,10],[4,8,5,7],[5,12,6,1],[8,11,9,12],[9,3,10,2]], bridges = {0:[6,7],1:[12,1]})
        knot.drag_crossing_under_bridge(knot.crossings[5], 3)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[1,6,2,7],0],[[2,14,3,13],1],[[4,8,5,7],0],[[5,16,6,1],1],[[8,15,9,16],1],[[9,15,10,14],1],[[10,4,11,3],None],[[11,12,12,13],1]]])
        self.assertEqual(knot, answer)

    # Dragging case b=g, a>y, y==h
    def testDragCrossingUnderBridge_7(self):
        knot = create_knot_from_pd_code([[7,3,8,2],[9,1,10,12],[11,4,12,5],[1,9,2,8],[3,7,4,6],[5,10,6,11]], bridges = {0:[3,2],1:[7,6]})
        knot.drag_crossing_under_bridge(knot.crossings[2], 4)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[9,3,10,2], 0], [[11,1,12,16], None], [[13,6,14,7], 1], [[14,3,15,4], 0], [[15,9,16,8], 1], [[1,11,2,10], None], [[4,8,5,7], 1], [[5,12,6,13], None]]])
        self.assertEqual(knot, answer)

    # Dragging case b=e, a>y, y==f
    def testDragCrossingUnderBridge_8(self):
        knot = create_knot_from_pd_code([[12,4,13,3],[13,1,14,18],[15,8,16,9],[16,5,17,6],[17,11,18,10],[1,4,2,5],[2,12,3,11],[6,10,7,9],[7,14,8,15]], bridges = {0:[4,5],1:[11,1]})
        knot.drag_crossing_under_bridge(knot.crossings[1], 1)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[14,4,15,3],0],[[15,4,16,5],0],[[16,2,17,1],None],[[17,7,18,6],0],[[19,10,20,11],1],[[20,7,21,8],0],[[21,13,22,12],1],[[22,5,1,6],0],[[2,14,3,13],1],[[8,12,9,11],1],[[9,18,10,19],None]]])
        self.assertEqual(knot, answer)

    # Dragging case b=e, a<y, y==f
    def testDragCrossingUnderBridge_9(self):
        knot = create_knot_from_pd_code([[4,13,5,14],[6,4,7,3],[8,11,9,12],[9,1,10,14],[12,5,13,6],[1,11,2,10],[2,8,3,7]], bridges = {0:[1,14], 1:[11,12]})
        knot.drag_crossing_under_bridge(knot.crossings[6], 8)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[6,17,7,18],0],[[8,6,9,5],None],[[9,14,10,15],1],[[11,1,12,18],0],[[16,7,17,8],None],[[1,13,2,12],1],[[2,13,3,14],1],[[3,11,4,10],None],[[4,16,5,15],1]]])
        self.assertEqual(knot, answer)

    # Dragging case d=g, a>y, y==h
    def testDragCrossingUnderBridge_10(self):
        knot = create_knot_from_pd_code([[2,12,3,11],[4,10,5,9],[6,2,7,1],[8,14,9,13],[10,4,11,3],[12,6,13,5],[14,8,1,7]], bridges = {0:[12,11],1:[6,5]})
        knot.drag_crossing_under_bridge(knot.crossings[3], 13)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[2,16,3,15],0],[[4,14,5,13],None],[[8,2,9,1],None],[[10,7,11,8],1],[[11,17,12,16],0],[[12,6,13,5],1],[[14,4,15,3],None],[[17,7,18,6],1],[[18,10,1,9],None]]])
        self.assertEqual(knot, answer)

    # Dragging case d=e, a>y, y==f
    def testDragCrossingUnderBridge_11(self):
        knot = create_knot_from_pd_code([[1,9,2,8],[3,12,4,13],[4,9,5,10],[5,15,6,14],[7,24,8,25],[10,14,11,13],[11,2,12,3],[15,18,16,19],[17,22,18,23],[19,27,20,26],[21,16,22,17],[23,1,24,28],[25,6,26,7],[27,21,28,20]], bridges = {0:[9,8],1:[12,1],2:[24,25]})
        knot.drag_crossing_under_bridge(knot.crossings[12], 7)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[1,9,2,8],0],[[3,12,4,13],1],[[4,9,5,10],0],[[5,15,6,14],1],[[6,25,7,26],2],[[10,14,11,13],1],[[11,2,12,3],None],[[15,18,16,19],None],[[17,22,18,23],None],[[19,31,20,30],None],[[21,16,22,17],None],[[23,1,24,32],None],[[27,26,28,27],2],[[28,7,29,8],0],[[29,25,30,24],2],[[31,21,32,20],None]]])
        self.assertEqual(knot, answer)

    # Dragging case d=e, a<y, y==f
    def testDragCrossingUnderBridge_12(self):
        knot = create_knot_from_pd_code([[1,9,2,8],[3,12,4,13],[4,9,5,10],[5,15,6,14],[6,25,7,26],[10,14,11,13],[11,2,12,3],[15,18,16,19],[17,22,18,23],[19,29,20,28],[21,16,22,17],[23,1,24,30],[26,7,27,8],[27,25,28,24],[29,21,30,20]], bridges = {0:[9,8],1:[12,1],2:[25,26]})
        knot.drag_crossing_under_bridge(knot.crossings[6], 3)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[1,9,2,8],0],[[2,15,3,16],1],[[4,9,5,10],0],[[5,19,6,18],1],[[6,29,7,30],2],[[10,18,11,17],1],[[11,16,12,17],1],[[12,3,13,4],None],[[13,15,14,14],1],[[19,22,20,23],None],[[21,26,22,27],None],[[23,33,24,32],None],[[25,20,26,21],None],[[27,1,28,34],None],[[30,7,31,8],0],[[31,29,32,28],2],[[33,25,34,24],None]]])
        self.assertEqual(knot, answer)

    # Dragging case b=g, a<y, y==f
    def testDragCrossingUnderBridge_13(self):
        knot = create_knot_from_pd_code([[2,23,3,24],[4,13,5,14],[6,22,7,21],[7,1,8,32],[8,18,9,17],[10,3,11,4],[11,26,12,27],[27,12,28,13],[14,29,15,30],[15,21,16,20],[16,32,17,31],[18,10,19,9],[19,30,20,31],[24,1,25,2],[25,22,26,23],[27,12,28,13],[28,6,29,5]], bridges = {0:[23,24],1:[1,2]})
        knot.drag_crossing_under_bridge(knot.crossings[6], 26)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[2,27,3,28],0],[[4,15,5,16],None],[[6,24,7,23],0],[[7,1,8,36],1],[[8,20,9,19],None],[[10,3,11,4],None],[[11,27,12,26],0],[[12,29,13,30],None],[[13,24,14,25],0],[[31,14,32,15],None],[[16,33,17,34],1],[[17,23,18,22],0],[[18,36,19,35],1],[[20,10,21,9],None],[[21,34,22,35],1],[[28,1,29,2],1],[[30,25,31,26],0],[[31,14,32,15],None],[[32,6,33,5],None]]])
        self.assertEqual(knot, answer)

    # Dragging case d=e, a<y, y==h
    def testDragCrossingUnderBridge_14(self):
        knot = create_knot_from_pd_code([[15,29,16,28],[17,24,18,25],[18,4,19,3],[20,7,21,8],[22,5,23,6],[23,14,24,15],[26,2,27,1],[29,17,30,16],[30,10,1,9],[4,14,5,13],[6,21,7,22],[8,28,9,27],[10,25,11,26],[11,3,12,2],[12,19,13,20]], bridges = {0:[29,28],1:[17,16]})
        knot.drag_crossing_under_bridge(knot.crossings[5], 15)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[14,32,15,31],0],[[17,26,18,27],None],[[18,4,19,3],None],[[20,7,21,8],None],[[22,5,23,6],None],[[23,31,24,30],0],[[24,15,25,16],1],[[25,32,26,33],0],[[28,2,29,1],None],[[33,17,34,16],1],[[34,10,1,9],None],[[4,14,5,13],None],[[6,21,7,22],None],[[8,30,9,29],0],[[10,27,11,28],None],[[11,3,12,2],None],[[12,19,13,20],None]]])
        self.assertEqual(knot, answer)

    # Dragging case d=e, a>y, y==h
    def testDragCrossingUnderBridge_15(self):
        knot = create_knot_from_pd_code([[15,35,16,34],[19,28,20,29],[20,4,21,3],[22,9,23,10],[24,7,25,8],[25,33,26,32],[26,17,27,18],[27,36,28,37],[30,2,31,1],[37,19,38,18],[38,12,1,11],[4,36,5,35],[5,17,6,16],[6,33,7,34],[8,23,9,24],[10,32,11,31],[12,29,13,30],[13,3,14,2],[14,21,15,22]], bridges = {0:[35,34],1:[17,18],2:[2,1]})
        knot.drag_crossing_under_bridge(knot.crossings[16], 30)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[19,39,20,38],0],[[23,32,24,33],None],[[24,6,25,5],2],[[26,11,27,12],None],[[28,9,29,10],None],[[29,37,30,36],0],[[30,21,31,22],1],[[31,40,32,41],0],[[33,3,34,2],2],[[41,23,42,22],1],[[42,14,1,13],None],[[6,40,7,39],0],[[7,21,8,20],1],[[8,37,9,38],0],[[10,27,11,28],None],[[12,36,13,35],0],[[14,2,15,1],2],[[15,34,16,35],0],[[16,3,17,4],2],[[17,5,18,4],2],[[18,25,19,26],None]]])
        self.assertEqual(knot, answer)

    # Dragging case b=e, a>y, y==h
    def testDragCrossingUnderBridge_16(self):
        knot = create_knot_from_pd_code([[15,37,16,36],[22,2,23,1],[23,32,24,33],[24,9,25,10],[26,7,27,8],[27,35,28,34],[28,17,29,18],[29,38,30,39],[30,4,31,3],[39,19,40,18],[40,19,41,20],[41,13,42,12],[42,22,1,21],[4,38,5,37],[5,17,6,16],[6,35,7,36],[8,25,9,26],[10,34,11,33],[11,20,12,21],[13,3,14,2],[14,31,15,32]], bridges = {0:[37,36],1:[17,18],2:[2,1]})
        knot.drag_crossing_under_bridge(knot.crossings[11], 13)
        answer = Knot([Crossing(x[0], x[1]) for x in [[[17,39,18,38],0],[[24,2,25,1],2],[[25,34,26,35],0],[[26,11,27,12],None],[[28,9,29,10],None],[[29,37,30,36],0],[[30,19,31,20],1],[[31,40,32,41],0],[[32,6,33,5],2],[[41,21,42,20],1],[[42,21,43,22],1],[[43,5,44,4],2],[[44,16,45,15],None],[[45,2,46,3],2],[[46,24,1,23],1],[[6,40,7,39],0],[[7,19,8,18],1],[[8,37,9,38],0],[[10,27,11,28],None],[[12,36,13,35],0],[[13,22,14,23],1],[[14,4,15,3],2],[[16,33,17,34],0]]])
        self.assertEqual(knot, answer)

class SimplifyRm1TestCase(unittest.TestCase):
    def testSimplifyRm1(self):
        knot = create_knot_from_pd_code([[1,5,2,4],[3,3,4,2],[6,6,7,5],[8,8,1,7]])
        knot.simplify_rm1([1])
        answer = create_knot_from_pd_code([[1,3,2,2],[4,4,5,3],[6,6,1,5]])
        self.assertEqual(knot, answer)

    def testSimplifyRm1_1(self):
        knot = create_knot_from_pd_code([[6,14,7,13],[10,16,11,15],[11,9,12,8],[12,6,13,5],[1,16,2,1],[2,10,3,9],[3,15,4,14],[4,8,5,7]])
        knot.simplify_rm1([4])
        answer = create_knot_from_pd_code([[4,12,5,11],[8,14,9,13],[9,7,10,6],[10,4,11,3],[14,8,1,7],[1,13,2,12],[2,6,3,5]])
        self.assertEqual(knot, answer)

    def testSimplifyRm1_2(self):
        knot = create_knot_from_pd_code([[3,6,4,7],[4,2,5,1],[5,2,6,3],[7,8,8,1]])
        knot.simplify_rm1([3])
        answer = create_knot_from_pd_code([[3,6,4,1],[4,2,5,1],[5,2,6,3]])
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

    def testSimplifyRm2Bridges(self):
        # Check bridge changes and PD code.
        knot = create_knot_from_pd_code([[8,19,9,20],[10,8,11,7],[11,16,12,17],[12,22,13,21],[18,9,19,10],[1,15,2,14],[2,15,3,16],[3,1,4,22],[4,14,5,13],[5,20,6,21],[6,18,7,17]], bridges = {0:[19,20],1:[18,17]})
        knot.simplify_rm2([5, 6], [[15, -2], [2, -2]])
        answer = Knot([Crossing(x[0], x[1]) for x in [[[6,15,7,16],0],[[8,6,9,5],None],[[9,12,10,13],1],[[10,18,11,17],0],[[14,7,15,8],None],[[1,1,2,18],0],[[2,12,3,11],1],[[3,16,4,17],0],[[4,14,5,13],1]]])
        self.assertEqual(knot, answer)
        self.assertEqual(knot.bridges, {0:[15,1],1:[14,11]})

class SimplifyRm2RecursivelyTestCase(unittest.TestCase):
    def testSimplifyRm2Recursively(self):
        knot = create_knot_from_pd_code([[1,13,2,12],[2,21,3,22],[3,14,4,15],[4,18,5,17],[5,25,6,24],[6,12,7,11],[7,22,8,23],[8,15,9,16],[9,17,10,16],[10,24,11,23],[18,26,19,25],[19,26,20,1],[20,14,21,13]])
        knot.simplify_rm2_recursively()
        answer = create_knot_from_pd_code([[1,5,2,4],[2,4,3,3],[6,6,1,5]])
        self.assertEqual(knot, answer)

if __name__ == '__main__':
    unittest.main()
