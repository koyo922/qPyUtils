#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
import sys
from unittest import TestCase

from qPyUtils.constant import INF


class TestConstant(TestCase):
    def test_inf(self):
        self.assertEqual(sys.maxsize, INF)
