#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
from __future__ import unicode_literals

import json
import re

import six
from typing import Pattern, Text, Iterable, Tuple

import dirtyjson


def is_none_or_empty(s):  # pragma: no cover
    return s is None or len(s) == 0


def dump_utf8(obj, indent=None):
    return json.dumps(obj, ensure_ascii=False, indent=indent)


def csplit(lines, pattern):
    # type: (Iterable[Text], Union[Pattern[Text], Text]) -> Iterable[Tuple[Text]]
    """
    模仿Linux Bash的csplit功能，对指定的文本流(line-wise)，按照pattern分组切分
    :param lines: 可迭代的文本流
    :param pattern: 正则pattern对象 或者 相应的文本
    :return:
    """
    buffer_lines = []
    if isinstance(pattern, six.string_types):
        pattern = re.compile(r'.*{}.*'.format(pattern))
    for line in lines:
        if pattern.match(line):
            if buffer_lines:
                yield tuple(buffer_lines)
            del buffer_lines[:]
        buffer_lines.append(line)

    if buffer_lines:
        yield tuple(buffer_lines)


def dirty_json_or_none(text):
    # type: (Text) -> dict
    try:
        return dirtyjson.loads(text)
    except dirtyjson.error.Error:
        # logger.warning('^^^^^^^^^^ malformed json text: %s', text)
        malformed_json_text.append(text)
        return None


def ensure_text(text, encoding='utf8'):
    if text is None:
        return None
    if isinstance(text, Text):
        return text
    if isinstance(text, six.binary_type):
        return six.text_type(text, encoding)
    raise AssertionError('unexpected arg type:{}'.format(type(text)))


malformed_json_text = []
