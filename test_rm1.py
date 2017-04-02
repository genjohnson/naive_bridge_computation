#!/usr/bin/env python2.7

import unittest
from rm1 import has_duplicate_value

class Rm1TestCase(unittest.TestCase):
    """Tests for `rm1.py`."""

    def test_has_duplicate_value(self):
        """Is [1,2,3,3] successfully determined to contain a duplicate value?"""
        self.assertNotEqual(has_duplicate_value([1,2,3,3]), False)
        """Is [1,2,3,4] successfully determined to not contain a duplicate value?"""
        self.assertFalse(has_duplicate_value([1,2,3,4]))
if __name__ == '__main__':
    unittest.main()
