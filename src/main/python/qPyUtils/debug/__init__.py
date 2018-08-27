#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
utils for debug

Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/8/20 下午10:21
"""
from contextlib import contextmanager
from typing import Tuple, Union, Any
from unittest import TestCase

from mockito import unstub, mock

from qPyUtils.constant import T


def auto_unstub(testcase):
    # type: (TestCase) -> TestCase
    """
    decorator for TestCase, adding ability to auto unstub mockito
    thanks: https://gist.github.com/jnape/5767029
    :param testcase:
    :return:
    """
    wrapped_tearDown = testcase.tearDown

    def newTeardown(self):
        try:
            wrapped_tearDown(self)
        except:  # noqa: E722  # pragma: no cover
            raise
        finally:
            unstub()

    testcase.tearDown = newTeardown
    return testcase


@contextmanager
def mockify(*args, **kwargs):
    # type: (Iterable[T], Any) -> Union[Tuple[T], T]
    """
    mockify multiple args, using specified attrs
    :param args: the objects to be mockified, usually (stdout, stderr)
    :param kwargs: the specified behaviour, e.g. dict(write=dummy_fn)
    :return: mockified version of args
    """
    args = [mock(dict(**kwargs)) for _ in args]
    try:
        yield args if len(args) > 1 else args[0]
    finally:
        unstub()
