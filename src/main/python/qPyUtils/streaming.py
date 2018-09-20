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

    def __init__(self, n_epoch=float('inf')):
        assert isinstance(n_epoch, Number) and n_epoch >= 1, \
            ('Usage:'
             '@Repeat(n_epoch=...)  # NOTE: init before use; `n_epoch` default to INF'
             'def my_generator_function():'
             '  ...')
        self.n_epoch = n_epoch
        self.gen_fn = None  # type: Callable[[Any], Generator]
        self.cur_iter = 0

    def __iter__(self):
        """
        as a re-enterable iterator
        """
        if self.cur_iter >= self.n_epoch:
            return
        for i in self.gen_fn():
            yield i
        self.cur_iter += 1

    def __call__(self, gen_fn, *args, **kwargs):
        """
        wrap the `gen_fn` along with args/kwargs as the factory of generator
        :param gen_fn: the generator factory (either as function or method)
        :param args: positional args for using in `gen_fn`
        :param kwargs: keyword args for using in `gen_fn`
        :return: self (which is iterable)
        """
        assert callable(gen_fn), 'Please feed in a *FACTORY FUNCTION/METHOD* for the generator,' \
                                 ' instead of the generator itself!'
        self.gen_fn = F(gen_fn, *args, **kwargs)
        return self

    def __get__(self, instance, owner):
        """
        For compatibility with methods (beside functions),
        it works like below:

        ```python
        #----- define
        class MyClazz(object):
            @Repeat(n_epoch=2) # ..... (1)
            def my_method(self, a, b, prefix='>>>'):
                for i in range(a, b):
                    yield '{}{}'.format(prefix, i)

        obj = MyClazz()
        my_gen = obj.my_method(0, 3, prefix=':') # ..... (2)

        #----- is equivalent to
        r = Repeat(n_epoch=2) # the `Repeat(n_epoch=2)` part at (1)
        MyClazz.my_method = r(MyClazz.my_method) # the `@` part at (1)
        got_fn = Repeat.__get__(r, obj, MyClazz) # the `obj.my_method` part at (2)
        my_gen = got_fn(0, 3, prefix=':') # the `(0, 3, prefix=':')` part at (2)
        ```
        :param instance: the calling object
        :param owner: not used
        :return:
        """
        bound_method = F(self.gen_fn, instance)
        return F(self, bound_method)  # use the bound-method as `gen_fn` for `self.__call__()`
