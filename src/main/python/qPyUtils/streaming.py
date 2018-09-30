#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
utils for streaming data process

Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/8/25 下午3:32
"""
from numbers import Number

import six
from fn import F
from typing import Sequence, Tuple, Union, Generator, Any, Callable

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


class Repeat(object):
    """
    A decorator class for wrapping a generator_factory;
    so that it could be iterated multiple epochs, just like a tuple/list
    """

    def __init__(self, raw_fn):
        """
        wrap the `raw_fn` as the factory of generator
        :param raw_fn: the generator factory (either as function or method)
        :return: self (which is iterable)
        """
        assert callable(raw_fn), 'Please feed in a *FACTORY FUNCTION/METHOD* for the generator,' \
                                 ' instead of the generator itself!'
        self.raw_fn = raw_fn  # may be a function or method
        self.bound_fn = None  # bound one (only meaningful for method)
        self.dst_fn = None  # the one for feed outputing
        self.cur_iter = 0

    def __call__(self, *args, **kwargs):
        """ setting the feeding source of self """
        # use self.bound_fn if available
        self.dst_fn = F((self.bound_fn or self.raw_fn), *args, **kwargs)
        return self

    def __iter__(self):
        for e in (self.dst_fn or self.bound_fn or self.raw_fn)():
            yield e
        self.cur_iter += 1

    def __get__(self, instance, owner):
        """
        For compatibility with methods (beside functions),
        it works like below:

        ```python
        #----- define
        class MyClazz(object):
            @Repeat # ..... (1)
            def my_method(self, a, b, prefix='>>>'):
                for i in range(a, b):
                    yield '{}{}'.format(prefix, i)

        obj = MyClazz()
        my_gen = obj.my_method(0, 3, prefix=':') # ..... (2)

        #----- is equivalent to
        r = Repeat # the `Repeat` part at (1)
        MyClazz.my_method = r(MyClazz.my_method) # the `@` part at (1)
        got_fn = Repeat.__get__(r, obj, MyClazz) # the `obj.my_method` part at (2)
        my_gen = got_fn(0, 3, prefix=':') # the `(0, 3, prefix=':')` part at (2)
        ```
        :param instance: the calling object
        :param owner: not used
        :return:
        """
        self.bound_fn = F(self.raw_fn, instance)
        return self
