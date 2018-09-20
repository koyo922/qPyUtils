#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
file system related utils

Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/9/11 下午11:09
"""
import os.path
import shutil

from qPyUtils import logger


def rm(path, ignore_errors=True):
    # type: (Text, bool) -> Text
    """
    equivalent to bash command `rm -f ${path}`; or `rm ${path}` if ignore_errors=False
    :param path: could either be relative or absolute.
    :param ignore_errors:
    """
    try:
        if not os.path.exists(path):
            raise OSError('^^^^^ path: {} not exist'.format(path))
        elif os.path.isfile(path):
            os.remove(path)  # remove the file
        elif os.path.isdir(path):
            shutil.rmtree(path)  # remove dir and all contains
        else:
            raise ValueError("path {} exists, but is neither a file nor dir.".format(path))  # pragma: no cover
        logger.debug('----- [DONE]path %s deleted', path)
        return path
    except (OSError, ValueError):
        if not ignore_errors:
            raise
