#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
参考百度编码规范 http://styleguide.baidu.com/style/python/index.html#%E7%BC%96%E7%A8%8B%E5%AE%9E%E8%B7%B5id9

Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/8/10 下午4:29
"""
import os
import sys
import logging
import logging.handlers


class _BelowWarningFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.WARNING


# noinspection PyIncorrectDocstring
def init_log(log_path, logger_name=None,
             level=logging.INFO, when="D", backup=365, to_console=True, show_logger_src=False,
             fmt="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s",
             datefmt="%m-%d %H:%M:%S"):
    """
    init_log - initialize log module

    Args:
      log_path      - Log file path prefix.
                      Log data will go to two files: log_path.log and log_path.log.wf
                      Any non-exist parent directories will be created automatically
      logger_name   - name of the logger to get, if None, return root logger
                      default value: None
                      Any non-exist parent directories will be created automatically
      level         - msg above the level will be displayed in *.log(always WARN for *.log.wf, DEBUG for stdout)
                      DEBUG < INFO < WARNING < ERROR < CRITICAL
                      the default value is logging.INFO
      when          - how to split the log file by time interval
                      'S' : Seconds
                      'M' : Minutes
                      'H' : Hours
                      'D' : Days
                      'W' : Week day
                      default value: 'D'
      backup        - how many backup file to keep
                      default value: 365
      to_console    - whether always write to console
                      default value: True
      show_logger_src
                    - show name and path for all loggers, including 3rd-party library,
                      used for debugging and silence those unwanted
                      default value: False
      fmt           - format of the log
                      default format:
                      %(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s
                      > INFO: 12-09 18:02:42: log.py:40 * 139814749787872 HELLO WORLD

    Return:
        logging.Logger: the logger object

    Raises:
        OSError: fail to create log directories
        IOError: fail to open log file
    """
    if show_logger_src:
        fmt = fmt.replace('%(filename)s:%(lineno)d', '[%(name)s@%(pathname)s]%(filename)s:%(lineno)d')
    formatter = logging.Formatter(fmt, datefmt)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    del logger.handlers[:]

    log_dir = os.path.dirname(log_path)
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log.debug",
                                                        when=when,
                                                        backupCount=backup)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log",
                                                        when=when,
                                                        backupCount=backup)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log.wf",
                                                        when=when,
                                                        backupCount=backup)
    handler.setLevel(logging.WARNING)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if to_console:
        handler_stdout = logging.StreamHandler(sys.stdout)
        handler_stdout.setLevel(logging.DEBUG)
        handler_stdout.addFilter(_BelowWarningFilter())  # 低于WARNING的打到 stdout
        handler_stdout.setFormatter(formatter)
        logger.addHandler(handler_stdout)

        handler_stderr = logging.StreamHandler(sys.stderr)
        handler_stderr.setLevel(logging.WARNING)  # >= WARNING的打到 stderr
        handler_stderr.setFormatter(formatter)
        logger.addHandler(handler_stderr)

    return logger
