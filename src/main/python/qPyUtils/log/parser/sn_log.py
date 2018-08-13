#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number

import re
from datetime import datetime

from fn import _ as X
from functional import seq
from pathlib import Path
from typing import Iterable

from qPyUtils.log.parser.base import BaseLogParser
from qPyUtils.text import csplit, dirty_json_or_none


class SnLogLoader(BaseLogParser):
    LOG_TYPE = 'sn_log'

    def glob_files(self, base_path):
        # type: (Path) -> Iterable[Path]
        return seq(base_path.rglob('voiceKeyboard/*.log'))

    def filepath2date(self, file_path):
        # type: (Path) -> datetime
        return datetime.strptime(file_path.stem, '%Y-%m-%d')

    def logfile2blocks(self, path):
        # type: (Path) -> Iterable[Text]
        with path.open(mode='rt', encoding='utf8') as lines:
            return seq(csplit(lines, re.compile(r'^{"vers'))).map(''.join)

    def block2records(self, block):
        # type: (Text) -> Iterable[dict]
        j = dirty_json_or_none(block)
        if j is None:
            yield None
        else:
            other_attrs = (seq(j.items())
                           .filter(X[0] != 'records')
                           .to_dict())
            for rec in j['records']:
                yield dict(**rec) | dict(**other_attrs)
