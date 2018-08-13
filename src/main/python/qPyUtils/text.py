#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number

from pathlib import Path
from typing import Pattern, Text, Iterable, Tuple

import dirtyjson


def csplit(file_path, pattern):
    # type: (Path, Pattern[Text]) -> Iterable[Tuple[Text]]
    """
    模仿Linux Bash的csplit功能，对指定的文件，安装pattern分组切分
    :param file_path:
    :param pattern:
    :return:
    """
    buffer = []
    with file_path.open(mode='rt', encoding='utf8') as f:
        for line in f:
            if pattern.match(line):
                if buffer:
                    yield tuple(buffer)
                buffer.clear()
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
