#!/usr/bin/env python2.7

def remove_tuple(crossing, knot):
  knot.remove(crossing)
  return knot

def remove_tuples(indices, knot):
  # Remove tuples from last to first to avoid changing
  # the index of tuples not yet processed.
  indices.sort(reverse = True)
  for index in indices:
    del(knot[index])
  return knot

def alter_elements_greater_than(knot, value, increment):
  for place, crossing in enumerate(knot):
    for index, element in enumerate(crossing):
      if element > value:
        crossing[index] = element + increment
  return knot

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
  twisted_crossings = []
  for index, crossing in enumerate(knot):
    duplicate_value = has_duplicate_value(crossing)
    if duplicate_value:
      twisted_crossings.append(index)
      alter_elements_greater_than(knot, duplicate_value, -2)
  if twisted_crossings:
    remove_tuples(twisted_crossings, knot)
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
    print 'the original knot is ' + str(knot)
    simplify_all_rm1(knot)
    print 'the simplified knot is ' + str(knot)
