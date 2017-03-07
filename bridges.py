#!/usr/bin/env python2.7

# If two elements in the tuple are equal (with value x)
  # Delete the tuple
  # Decrease all elements with value greater than x
  # print "The tuple [] has been eliminated"
# return knot  

def remove_tuple(crossing, knot):  
  knot.remove(crossing)
  return knot

def alter_elements_greater_than(knot, value, increment):
  for place, crossing in enumerate(knot):
    for index, element in enumerate(crossing):
      if element > value:
        crossing[index] = element + increment
  return knot

def has_twist(crossing):
  duplicate_value = has_duplicate_value(crossing)
  if duplicate_value:
    return True
  else:
    return False

def has_duplicate_value(crossing):
  sets = reduce(
    lambda (u, d), o : (u.union([o]), d.union(u.intersection([o]))),
    crossing,
    (set(), set()))

  if sets[1]:
    return list(sets[1])[0]
  else:
    return False

def simplify_all_rm1(knot):
  for crossing in knot:
    duplicate_value = has_duplicate_value(crossing)
    if duplicate_value:
      remove_tuple(crossing, knot)
      alter_elements_greater_than(knot, duplicate_value, -2)
  return knot

# Read in a CSV.
import ast
import csv
with open('knots.csv') as csvfile:
  fieldnames = ['name', 'pd_notation']
  knotreader = csv.DictReader(csvfile)

  for row in knotreader:
    # Evaluate strings containing Python lists.
    knot = ast.literal_eval(row['pd_notation'])
    # Check if the knot contains any twists.
    simplify_all_rm1(knot)
