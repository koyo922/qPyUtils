#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number

################################################################################
#
# Copyright (c) 2018 Baidu.com, Inc. All Rights Reserved
#
################################################################################

"""
pybuilder config

Authors: qianweishuo<qianweishuo@baidu.com>
Date:    2018/8/10 下午4:46
"""
from io import open

import yaml
from pybuilder.cli import ColoredStdOutLogger
from pybuilder.core import use_plugin, init, Project, Author

use_plugin('python.core')
use_plugin("pypi:pybuilder_read_profile_properties")
use_plugin('python.install_dependencies')
use_plugin('python.flake8')
use_plugin('python.unittest')
use_plugin('python.coverage')
use_plugin("filter_resources")
use_plugin("python.distutils")
use_plugin('copy_resources')

default_task = ['install_dependencies', 'publish']

# 注意这些基本属性还是不要写进yaml文件；它们跟property不同，不方便update进project对象
name = 'qPyUtils'
authors = [Author('Qian Weishuo ', 'qzy922@gmail.com'), ]
license = 'MIT License'
summary = 'some handy tools for python / bash'
description = 'python and bash utils, by qianws and his collection'
url = 'https://github.com/koyo922/qPyUtils'
version = '0.1.0.dev'


@init
def init(project, logger):
    # type: (Project, ColoredStdOutLogger) -> None
    """
    加载默认的配置文件，然后加载各种profile下的
    :param project:
    :param logger:
    :return:
    """
    with open('configs/properties.yml', 'r') as f:
        project.properties.update(yaml.load(f))

    project.depends_on_requirements("requirements.txt")
    project.build_depends_on_requirements("requirements-dev.txt")
