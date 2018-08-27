#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
import math
import sys
from unittest import TestCase

from mockito import verify

from qPyUtils.debug import mockify
from qPyUtils.parallel import para


# CAUTION: if used in pool_type='process' (not 'thread');
# then `fn()` must be independent of the para calling code.
# reason unclear
def fn(x, y=0):
    if x == 4 and y == 2:  # just for verify raise behavior
        raise AssertionError
    return math.factorial(x) + y


class TestParallel(TestCase):
    def test_para(self):
        arr = list(range(8))
        expected = [1, 1, 2, 6, 24, 120, 720, 5040]

        # CAUTION: some case might fail in PyCharm debug mode, but works on console
        # please ignore it

        # verify logic and is_suppress_progressbar
        with mockify(sys.stderr) as sys.stderr:  # temporarily suppress stderr
            self.assertEqual(expected, para(arr, fn, is_suppress_progressbar=False))
            verify(sys.stderr, atleast=1).write(Ellipsis)
        with mockify(sys.stderr) as sys.stderr:  # temporarily suppress stderr
            self.assertEqual(expected, para(arr, fn, is_suppress_progressbar=True))
            verify(sys.stderr, times=0).write(Ellipsis)

        # verify single thread --- sequential
        self.assertEqual(expected, para(arr, fn, n_jobs=1))

        # verify front_num=0
        self.assertEqual(expected, para(arr, fn, front_num=0))

        # verify `use_kwargs` format
        self.assertEqual(expected, para([{'x': a} for a in arr], fn, use_kwargs=True))

        # verify `args` format; `pool_type='process'` might fail for Pycharm debug mode
        self.assertEqual([e + 1 for e in expected], para([(a, 1) for a in arr], fn, pool_type='thread'))

        # verify raise behavior WITHIN front_num
        with self.assertRaises(AssertionError):
            para([(a, 2) for a in arr], fn, pool_type='thread', front_num=5)

        # verify raise behavior AFTER front_num
        res = para([(a, 2) for a in arr], fn, pool_type='thread', front_num=3)
        self.assertEqual(AssertionError, type(res[4]))
        self.assertEqual([e + 2 for i, e in enumerate(expected) if i != 4],
                         [r for i, r in enumerate(res) if i != 4])
