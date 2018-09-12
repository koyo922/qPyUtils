#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/9/12 下午10:20
"""
from __future__ import unicode_literals, print_function
import sys
import time
from unittest import TestCase

from mockito import verify, contains

import qPyUtils.log.timer
from qPyUtils.debug import mockify


class TestTimer(TestCase):
    def test_timer(self):
        # user-defined outout_fn; recur
        res = []
        with qPyUtils.log.timer.Timer('Long task 中文', output_fn=res.append) as timer:
            with timer.child('large step'):
                time.sleep(0.1)
            for _ in range(5):
                with timer.child('small step'):
                    time.sleep(0.05)
        self.assertRegexpMatches(res[0], r'Long task 中文: 0.3\d+s\n'
                                         r'  5x small step: 0.2\d+s \(7\d%\)\n'
                                         r'  1x large step: 0.1\d+s \(2\d%\)')

        # user-defined fmt; stdout
        with mockify(sys.stdout) as sys.stdout:
            with qPyUtils.log.timer.Timer('Long task 中文', fmt='{name} --> {elapsed:.3f}') as timer:
                time.sleep(0.1)
            # print('\n'.join(timer.format()), file=sys.stderr)
            verify(sys.stdout).write(contains('Long task 中文 --> 0.1'))
