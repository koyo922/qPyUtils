#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
from __future__ import unicode_literals
import re

import six
from typing import Pattern, Text, Iterable, Tuple

import dirtyjson


def csplit(lines, pattern):
    # type: (Iterable[Text], Union[Pattern[Text], Text]) -> Iterable[Tuple[Text]]
    """
    模仿Linux Bash的csplit功能，对指定的文本流(line-wise)，按照pattern分组切分
    :param lines: 可迭代的文本流
    :param pattern: 正则pattern对象 或者 相应的文本
    :return:
    """
    buffer = []
    if isinstance(pattern, six.string_types):
        pattern = re.compile(r'.*{}.*'.format(pattern))
    for line in lines:
        if pattern.match(line):
            if buffer:
                yield tuple(buffer)
            del buffer[:]
        buffer.append(line)

    if buffer:
        yield tuple(buffer)


def dirty_json_or_none(text):
    # type: (Text) -> dict
    try:
        return dirtyjson.loads(text)
    except dirtyjson.error.Error:
        # logger.warning('^^^^^^^^^^ malformed json text: %s', text)
        malformed_json_text.append(text)
        return None


malformed_json_text = []
