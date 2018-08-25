#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/8/10 下午4:45
"""
import logging
import shutil
import sys
from unittest import TestCase

from mockito import verify, contains, mock
from pathlib import Path

from qPyUtils.constant import dummy_fn
from qPyUtils.debug import auto_unstub, mockify
from qPyUtils.log import writer


@auto_unstub
class TestInitLog(TestCase):
    log_file_stem = './log/test_logger_init'

    def test_easy_path(self):
        logger = writer.init_log(None, self.log_file_stem, level=logging.INFO, is_show_logger_src=False,
                                 fmt="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s",
                                 datefmt="%m-%d %H:%M:%S", is_writing_console=False)

        with Path(self.log_file_stem).with_suffix('.log').open() as f:
            logger.info('test logger')
            self.assertRegexpMatches(f.readlines()[-1], '.*test logger')
        shutil.rmtree(Path(self.log_file_stem).parent.as_posix())

    def test_show_logger_src(self):
        LOGGER_NAME = "dummy_logger"

        sys.stderr = mock({'write': dummy_fn})  # clean console; CAUTION: before the 3rd-party logger

        # 3rd-party logger
        logger = logging.getLogger(LOGGER_NAME)
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)

        with mockify(sys.stderr) as sys.stderr:
            # add handlers for root logger; catching any specific loggers
            writer.init_log(LOGGER_NAME, self.log_file_stem, is_show_logger_src=True)
            # using specific(may be 3rd-party) logger
            logger.warning('dummy warning')
            # verify stderr
            verify(sys.stderr, times=1).write(contains(LOGGER_NAME))
