#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
utils for streaming data process

Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/8/25 下午3:32
"""
from typing import Sequence, Tuple, Union

from qPyUtils.constant import T


def try_flatten(sequence):
    # type: (Sequence[T]) -> Union[T, Sequence[T]]
    """
    trying to flatten a sequence;
    - if it is none or empty, return none
    - if len(it)==1, return it's only element(FLATTEN)
    - if len(it)>1, return itself untouched
    :param sequence:
    :return:
    """
    if sequence is None or len(sequence) == 0:  # pragma: no cover
        return None
    if len(sequence) == 1:
        return tuple(sequence)[0]
    return sequence


def try_tuple(obj):
    # type: (Union[T, Tuple[T]]) -> Tuple[T]
    if isinstance(obj, tuple):
        return obj

    return obj,  # NOTE the comma, made into tuple
