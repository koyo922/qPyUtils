#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
import sys
from unittest import TestCase

from qPyUtils.constant import INF, identity_fn, true_fn


class TestConstant(TestCase):
    def test_inf(self):
        self.assertEqual(sys.maxsize, INF)

    def test_identity(self):
        obj = dict(key='val')
        self.assertEqual(obj, identity_fn(obj))

    def test_true(self):
        self.assertTrue(true_fn([]))
        self.assertTrue(true_fn({}))
        self.assertTrue(true_fn(None))
        self.assertTrue(true_fn())
