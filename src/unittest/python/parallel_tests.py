#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
import math
import sys
from unittest import TestCase

from qPyUtils.debug import mockify
from qPyUtils.parallel import para


class TestParallel(TestCase):
    def test_para(self):
        arr = list(range(8))
        fn = math.factorial

        with mockify(sys.stderr) as sys.stderr:
            self.assertEqual([1, 1, 2, 6, 24, 120, 720, 5040], para(arr, fn))
