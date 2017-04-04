# #!/usr/bin/env python2.7

import ast
import csv
from common import *

def has_duplicate_value(crossing):
    """Find duplicate values in the PD notation of a crossing.

    Arguments:
    crossing -- (list) the PD notation of a crossing
    """
    sets = reduce(
        lambda (u, d), o : (u.union([o]), d.union(u.intersection([o]))),
        crossing,
        (set(), set()))
    if sets[1]:
        return list(sets[1])[0]
    else:
        return False

def simplify_rm1(twisted_crossings, knot):
    """Simplify one level of a knot by Reidemeister moves of type 1.

    Arguments:
    twisted_crossings -- (list) the indices of crossings to eliminate
    knot -- (object) a knot
    """
    for index in twisted_crossings:
        duplicate_value = has_duplicate_value(knot.crossings[index].pd_code)
        alter_elements_greater_than(knot, duplicate_value, -2)

    remove_tuples(twisted_crossings, knot)
    return knot

def check_rm1(knot):
    """Inspect a knot for crossings that can be eliminated
    by Reidemeister moves of type 1.

    Arguments:
    knot -- (object) a knot
    """
    twisted_crossings = []
    for index, crossing in enumerate(knot.crossings):
        duplicate_value = has_duplicate_value(crossing.pd_code)
        if duplicate_value:
            twisted_crossings.append(index)
    if twisted_crossings:
        return (twisted_crossings, knot)
    else:
        return False

def simplify_rm1_recursive(knot):
    """Simplify a knot by Reidemeister moves of type 1 until
    no more moves are possible.

    >>> simplify_rm1_recursive([[1, 5, 2, 4], [3, 3, 4, 2], [6, 6, 7, 5], [8, 8, 1, 7]])
    []
    >>> simplify_rm1_recursive([[1, 5, 2, 4], [3, 3, 4, 2], [7, 10, 8, 1], [8, 6, 9, 5], [9, 6, 10, 7]])
    [[3, 6, 4, 1], [4, 2, 5, 1], [5, 2, 6, 3]]

    Arguments:
    knot -- the PD notation of a knot
    """
    while True:
        moves_possible = check_rm1(knot)
        if moves_possible:
            simplify_rm1(moves_possible[0], moves_possible[1])
        if not moves_possible:
            break;
    return knot

# if __name__ == '__main__':
#     import doctest
#     doctest.testmod()
