#!/usr/bin/env python2.7

import ast
import csv
import common

def has_duplicate_value(crossing):
    """Find duplicate values in the PD notation of a crossing.

    >>> has_duplicate_value([1, 2, 3, 4])
    False
    >>> has_duplicate_value([1, 2, 3, 3])
    3

    Arguments:
    crossing -- the PD notation of a crossing
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

    >>> simplify_rm1([1, 2, 3], [[1, 5, 2, 4], [3, 3, 4, 2], [6, 6, 7, 5], [8, 8, 1, 7]])
    [[1, 3, 2, 2]]
    >>> simplify_rm1([0], [[1, 1, 2, 2]])
    []

    Arguments:
    twisted_crossings -- a list of indices of crossings to eliminate
    knot -- the PD notation of a knot
    """
    for index in twisted_crossings:
        duplicate_value = has_duplicate_value(knot[index])
        alter_elements_greater_than(knot, duplicate_value, -2)

    remove_tuples(twisted_crossings, knot)
    return knot

def check_rm1(knot):
    """Inspect a knot for crossings that can be eliminated
    by Reidemeister moves of type 1.

    >>> check_rm1([[3, 6, 4, 1], [4, 2, 5, 1], [5, 2, 6, 3]])
    False
    >>> check_rm1([[1, 5, 2, 4],[3, 3, 4, 2],[6, 6, 7, 5],[8, 8, 1, 7]])
    ([1, 2, 3], [[1, 5, 2, 4], [3, 3, 4, 2], [6, 6, 7, 5], [8, 8, 1, 7]])

    Arguments:
    knot -- the PD notation of a knot
    """
    twisted_crossings = []
    for index, crossing in enumerate(knot):
        duplicate_value = has_duplicate_value(crossing)
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

# Read in a CSV.
with open('knots.csv') as csvfile:
    fieldnames = ['name', 'pd_notation']
    knotreader = csv.DictReader(csvfile)

    for row in knotreader:
        # Evaluate strings containing Python lists.
        knot = ast.literal_eval(row['pd_notation'])
        # Check if the knot contains any twists.
        simplify_rm1_recursive(knot)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
