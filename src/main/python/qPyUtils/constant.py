# coding=utf-8
"""
constant values

Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/8/13 上午11:36
"""

import sys

from typing import TypeVar, Any

INF = sys.maxsize


def dummy_fn(*args, **kwargs):
    # type: (Any, Any) -> None
    """
    blackhole, just return None for anything
    :param args:
    :param kwargs:
    :return:
    """
    pass


T = TypeVar('T')


def identity_fn(arg):
    # type: (T) -> T
    """
    identity function; just return anything back
    :param arg:
    :return:
    """
    return arg


# noinspection PyUnusedLocal
def true_fn(*args, **kwargs):
    # type: (Any, Any) -> True
    return True
