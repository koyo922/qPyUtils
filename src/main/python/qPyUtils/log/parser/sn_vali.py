#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
sn_validate 类型的日志解析器

Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/8/4 下午6:09
"""
from datetime import datetime

import filelike
import pandas as pd
from functional import seq
from pathlib import Path
from typing import Iterable

from qPyUtils.log.parser.base import BaseLogParser, logger


class SnValiLoader(BaseLogParser):
    LOG_TYPE = 'sn_vali'

    def glob_files(self, base_path):
        # type: (Path) -> Iterable[Path]
        return seq(base_path.rglob('*_list.txt'))

    def filepath2date(self, file_path):
        # type: (Path) -> datetime
        return datetime.strptime(file_path.stem.rstrip('_list'), '%Y%m%d')

    def logfile2blocks(self, path):
        pass

    def block2records(self, block):
        pass

    def load_single_file(self, path=None):
        """ sn_vali这类日志比较特殊，近似于标准的csv；直接read_csv效率比较高 """
        assert path.is_file()
        with filelike.wrappers.Translate(path.open(mode='rt', encoding='utf8'),
                                         rfunc=lambda x: x.replace('\n\\n', '')) as f:
            df = pd.read_csv(f, dtype={'label2': int}, sep='\t', nrows=self.take_head)
        logger.info('---------- done loading[%s]: %s', self.LOG_TYPE, path.as_posix())
        return df
