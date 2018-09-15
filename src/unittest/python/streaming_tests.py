#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/9/14 下午10:33
"""
from __future__ import unicode_literals

from unittest import TestCase

from qPyUtils.streaming import Repeated


class TestStreaming(TestCase):

    def test_repeated_deco_fn(self):
        # trying to decorate before __init__
        with self.assertRaisesRegexp(AssertionError, 'init before use'):
            @Repeated
            def my_gen_err():
                yield 1
                yield 2

        # correctly decorate a function
        @Repeated(n_epoch=2)
        def my_gen():
            for i in range(3):
                yield i

        # first 2 epochs as expected
        self.assertEqual((0, 1, 2), tuple(my_gen))
        self.assertEqual((0, 1, 2), tuple(my_gen))
        # 3rd epoch is empty
        self.assertEqual(tuple(), tuple(my_gen))

    def test_repeated_deco_method(self):

        class MyClazz(object):
            @Repeated(n_epoch=2)
            def my_method(self, a, b, prefix='>>>'):
                for i in range(a, b):
                    yield '{}{}'.format(prefix, i)

        obj = MyClazz()
        my_gen = obj.my_method(0, 3, prefix=':')

        self.assertEqual((':0', ':1', ':2'), tuple(my_gen))
        self.assertEqual((':0', ':1', ':2'), tuple(my_gen))
        self.assertEqual(tuple(), tuple(my_gen))

    def test_repeated_hand_wrap(self):
        def my_gen():
            for i in range(3):
                yield i

        # try wrapping a generator instead of its factory
        with self.assertRaisesRegexp(AssertionError, '.*FACTORY FUNCTION/METHOD.*'):
            Repeated()(my_gen())

        # hand wrap a generator function
        r = Repeated(n_epoch=2)(my_gen)  # note: there is no extra parenthesis after `my_gen`
        self.assertEqual((0, 1, 2), tuple(r))
        self.assertEqual((0, 1, 2), tuple(r))
        self.assertEqual(tuple(), tuple(r))
