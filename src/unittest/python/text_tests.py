#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
import re
from unittest import TestCase

from qPyUtils.text import csplit, dirty_json_or_none, malformed_json_text


class TestText(TestCase):
    def test_dirty_json_or_none(self):
        # nice case
        j = dirty_json_or_none('{"name": "robin", "age": 18}')
        self.assertEqual(j, {"name": "robin", "age": 18})

        # dirty case
        j = dirty_json_or_none('{name: "robin", age:\n 18 }')
        self.assertEqual(j, {"name": "robin", "age": 18})

        # malformed case
        malformed_line = '{ na me: "rob"in", age:\n 0x18 }'
        j = dirty_json_or_none(malformed_line)
        self.assertIsNone(j)
        self.assertIn(malformed_line, malformed_json_text)

    def test_csplit(self):
        lines = [
            'line1',
            '---- line2',
            'line3',
            'line4',
            '---- line5',
            'line6'
        ]

        # string case
        self.assertEqual([('line1',), ('---- line2', 'line3', 'line4'), ('---- line5', 'line6')],
                         list(csplit(lines, r'----')))

        # regex case
        self.assertEqual([('line1', '---- line2'), ('line3', 'line4', '---- line5'), ('line6',)],
                         list(csplit(lines, re.compile(r'line[36].*'))))
