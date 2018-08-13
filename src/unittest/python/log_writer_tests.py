#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/8/10 下午4:45
"""
from unittest import TestCase

from pathlib import Path
import logging
import shutil

from qPyUtils.log import writer


class TestInitLog(TestCase):
    log_file_stem = './log/test_logger_init'

    def test_init_log(self):
        logger = writer.init_log(self.log_file_stem, logger_name=__name__,
                                 level=logging.INFO, show_logger_src=False,
                                 fmt="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s",
                                 datefmt="%m-%d %H:%M:%S")

        with Path(self.log_file_stem).with_suffix('.log').open() as f:
            logger.info('test logger')
            self.assertRegexpMatches(f.readlines()[-1], '.*test logger')

        shutil.rmtree(Path(self.log_file_stem).parent.as_posix())
