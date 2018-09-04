#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/9/2 下午6:31
"""
from __future__ import unicode_literals

import sys
import tempfile
import time
from io import open
from threading import Thread
from unittest import TestCase

import requests
import six
from docopt import DocoptExit

from qPyUtils.debug import start_in_thread
from qPyUtils.system import portforward


class TestSystemUtils(TestCase):

    def test_portforward(self):



        # ---------- empty args_in should raise 'Usage'
        with self.assertRaises(DocoptExit):
            del sys.argv[:]
            portforward.main()

        # ---------- test if config file works
        with tempfile.NamedTemporaryFile() as tmp:
            with open(tmp.name, 'wt+', encoding='utf8') as f:
                f.write("""
            www.pku-hall.com	80	8011
            www.nic.ad.jp	80	8012
            中国互联网络信息中心.中国	80	8013
            """.strip())
            sys.argv = ['porforward', '-c', tmp.name]

            start_in_thread(portforward.main)  # might automatically stop when unittest finish

            time.sleep(0.1)  # waiting server to start, critical for Travis-CI
            expected_prefix = "<title>首页——北京大学百周年纪念讲堂</title>"
            actual_response = requests.get('http://localhost:8011').content.decode('utf8')
            self.assertTrue(expected_prefix in actual_response)

        # ---------- test if command line args works
        sys.argv = ['porforward', '-H', 'www.nic.ad.jp', '-p', '80', '-l', '8015']

        # _thread.start_new_thread(portforward.main, tuple())
        start_in_thread(portforward.main)

        time.sleep(0.1)  # waiting server to start, critical for Travis-CI
        expected_prefix = """<!DOCTYPE html>
<html class="no-js" lang="en">
  <head>
    <meta charset="utf-8">
    <!--[if ie]><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"><![endif]-->
    <title>Japan Network Information Center - JPNIC</title>
    <meta name="author" content="Japan Network Information Center">"""
        actual_response = requests.get('http://localhost:8015').content.decode('utf8')
        self.assertTrue(actual_response.startswith(expected_prefix))