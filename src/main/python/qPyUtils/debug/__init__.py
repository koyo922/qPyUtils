#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
utils for debug

Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/8/20 下午10:21
"""
from unittest import TestCase

from mockito import unstub


def auto_unstub(test_suite):
    # type: (TestCase) -> TestCase
    """
    decorator for TestCase, adding ability to auto unstub mockito
    thanks: https://gist.github.com/jnape/5767029
    :param test_suite:
    :return:
    """
    wrapped_tearDown = test_suite.tearDown if 'tearDown' in dir(test_suite) else lambda self: True

    def tearDown(self):
        try:
            wrapped_tearDown(self)
        except:  # noqa: E722
            raise
        finally:
            unstub()

    test_suite.tearDown = tearDown
    return test_suite
