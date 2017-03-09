#!/usr/bin/env python2.7

import ast
import csv

def remove_tuples(indices, knot):
    """Remove tuples from the PD notation of a knot.

    >>> remove_tuples([1,3], [[4, 2, 5, 1], [8, 6, 1, 5], [6, 3, 7, 4], [2, 7, 3, 8]])
    [[4, 2, 5, 1], [6, 3, 7, 4]]

    Arguments:
    indices -- the list of indices of the tuples to remove
    knot -- the knot from which to remove tuples
    """
    # Remove tuples from last to first to avoid changing
    # the index of tuples not yet processed.
    indices.sort(reverse = True)
    for index in indices:
        del(knot[index])
    return knot

def alter_elements_greater_than(knot, value, increment):
    """Change the value of elements in the PD notation of a knot
    which are greater than some value.

    >>> alter_elements_greater_than([[4, 2, 5, 1], [8, 6, 1, 5], [6, 3, 7, 4], [2, 7, 3, 8]], 4, -2)
    [[4, 2, 3, 1], [6, 4, 1, 3], [4, 3, 5, 4], [2, 5, 3, 6]]
    >>> alter_elements_greater_than([[4, 2, 5, 1], [8, 6, 1, 5], [6, 3, 7, 4], [2, 7, 3, 8]], 4, 2)
    [[4, 2, 7, 1], [10, 8, 1, 7], [8, 3, 9, 4], [2, 9, 3, 10]]

    Arguments:
    knot -- the knot in which to alter elements
    value -- the integer against which to compare each element
    increment -- the integer to add to all elements greater than value
    """
    for place, crossing in enumerate(knot):
        for index, element in enumerate(crossing):
            if element > value:
                crossing[index] = element + increment
    return knot

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
        print 'the original knot is ' + str(knot)
        simplify_rm1_recursive(knot)
        print 'the simplified knot is ' + str(knot)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
