#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/8/25 下午11:21
"""
from __future__ import unicode_literals

import json
import time
import warnings
from threading import Thread
from unittest import TestCase

import requests
from mockito import when

import qPyUtils.web
from qPyUtils.debug import mockify
from qPyUtils.web import RESTful


class TestWeb(TestCase):
    def test_restful_wrapper(self):
        info_args = []
        with mockify(qPyUtils.web.logger, info=lambda *args: info_args.append(args)) as qPyUtils.web.logger:
            with when(warnings).warn(Ellipsis):  # temporarily suppress warning
                # setup and start the server
                @RESTful(port=8004, route='/')
                def introduce(name, friends):
                    return '{} has friends: {}'.format(name.upper(), ', '.join(friends))

                mock_server_thread = Thread(target=introduce.serve)
                mock_server_thread.setDaemon(True)
                mock_server_thread.start()  # automatically stopped when unittest finish

            # make a request from the client
            time.sleep(0.2)  # waiting server to start, critical for Travis-CI
            response_post = requests.post('http://localhost:8004',
                                          data={'name': 'koyo', 'friends': ['tsuga', 'Uncle.Li', '肉饼']})
            response_get = requests.get('http://localhost:8004',
                                        data={'name': 'koyo', 'friends': ['tsuga', 'Uncle.Li', '肉饼']})
            # assert correct response on client side
            self.assertEqual('KOYO has friends: tsuga, Uncle.Li, 肉饼', response_post.text)
            self.assertEqual('KOYO has friends: tsuga, Uncle.Li, 肉饼', response_get.text)

            # assert correct logging on server side
            # tried to use mockito.matchers.match(...); but found a bug for treating type unicode as not match
            self.assertRegexpMatches(info_args[0][0], u'---------- serving `introduce` at .*:8004')
            self.assertEqual(info_args[1][0], '----- got request_param: %s')
            self.assertEqual(json.loads(info_args[1][1]), {"friends": ["tsuga", "Uncle.Li", "肉饼"], "name": "koyo"})
