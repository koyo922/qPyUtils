#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
Timing related utils
ref: https://github.com/mherrmann/timer-cm/blob/master/timer_cm.py

Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/9/12 下午10:07
"""
from __future__ import unicode_literals, division

import sys
from decimal import Decimal
# noinspection PyProtectedMember
from timeit import default_timer

from typing import Text, Dict, Callable, Any, Union, List

from qPyUtils.constant import dummy_fn


class Timer(object):
    """
    a context manager for calculating the running time of a piece of code block
    """

    def __init__(self, name, output_fn='stdout', fmt=None):
        # type: (Text, Union[Text, Callable[[Text], Any]], Text) -> None
        """
        :param name: name of the task
        :param output_fn: the function used to output statistics; 'stdout'/'dummy'/any_other_function
        :param fmt: the format string; if None, use default `format()` method; else `fmt.format(**self.__dict__)`
        """
        self.name = name
        if output_fn is None or output_fn == 'dummy':
            self.output_fn = dummy_fn
        elif output_fn == 'stdout':
            self.output_fn = sys.stdout.write
        else:
            self.output_fn = output_fn
        if fmt is not None:  # overwrite the default `format()` method
            self.format = lambda: [fmt.format(**self.__dict__)]
        self.elapsed = Decimal()  # using Decimal for better precision ?
        self._start_time = None
        self._children = {}  # type: Dict[Text, Timer] # subtasks
        self._count = 0  # how many times re-entered

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()
        self.output_fn('\n'.join(self.format()))

    def child(self, name):
        try:
            return self._children[name]  # try to reuse (so that the `_count` field make sense)
        except KeyError:
            result = Timer(name, output_fn='dummy')
            self._children[name] = result
            return result

    def start(self):
        self._count += 1
        self._start_time = self.now

    def stop(self):
        self.elapsed += self.now - self._start_time  # add to `elapsed` field; accumulated if re-entered

    def format(self, indent=2):
        # type: (int) -> List[Text]
        """
        Format self into a tuple of lines; like:

        Long task 中文: 3.53s
          5x small step: 2.52s (71%)
          1x large step: 1.00s (28%)
        :param indent:
        :return:
        """
        children = self._children.values()
        elapsed = self.elapsed or sum(c.elapsed for c in children)  # pragma: no cover # self.elapsed never be zero
        my_lines = ['{}: {:.3}s'.format(self.name, elapsed)]
        # get how many digits needed for holding the `counts`
        max_count = max(c._count for c in children) if children else 1
        count_digits = len(str(max_count))
        for child in sorted(children, key=lambda c: c.elapsed, reverse=True):
            # get the lines of this child
            lines = child.format(indent)
            # modify the headline
            lines[0] = ('{}x '.format(child._count).rjust(count_digits) +  # how many times
                        lines[0] +  # original line
                        ' ({:.0f}%)'.format(child.elapsed / elapsed * 100))  # percentage
            # indent all lines
            for line in lines:
                my_lines.append((' ' * indent) + line)
        return my_lines

    @property
    def now(self):
        return Decimal(default_timer())
