#!/usr/bin/env python2.7

def alter_elements_greater_than(knot, value, increment):
    """Change the value of elements in the PD notation of a knot
    which are greater than some value.

    >>> alter_elements_greater_than([[4, 2, 5, 1], [8, 6, 1, 5], [6, 3, 7, 4], [2, 7, 3, 8]], 4, -2)
    [[4, 2, 3, 1], [6, 4, 1, 3], [4, 3, 5, 4], [2, 5, 3, 6]]
    >>> alter_elements_greater_than([[4, 2, 5, 1], [8, 6, 1, 5], [6, 3, 7, 4], [2, 7, 3, 8]], 4, 2)
    [[4, 2, 7, 1], [10, 8, 1, 7], [8, 3, 9, 4], [2, 9, 3, 10]]

    Arguments:
    knot -- (object) the knot in which to alter elements
    value -- (int) the number against which to compare each element
    increment -- (int) the number to add to all elements greater than value
    """
    for place, crossing in enumerate(knot.crossings):
        for index, element in enumerate(crossing.pd_code):
            if element > value:
                crossing.pd_code[index] = element + increment
    return knot

def remove_tuples(indices, knot):
    """Remove crossings from a knot.

    Arguments:
    indices -- (list) the indices of the crossings to remove
    knot -- (object) the knot from which to remove crossings
    """
    # Remove crossings from last to first to avoid changing
    # the index of crossings not yet processed.
    crossings = knot.crossings
    indices.sort(reverse = True)
    for index in indices:
        del crossings[index]
    knot.crossings = crossings
    
    return knot
