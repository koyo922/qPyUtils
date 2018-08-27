#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
import re
from unittest import TestCase

from qPyUtils.text import csplit, dirty_json_or_none, malformed_json_text, ensure_text


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
        # string case: empty last buffer
        self.assertEqual([], list(csplit([], r'----')))

        # string case
        self.assertEqual([('line1',), ('---- line2', 'line3', 'line4'), ('---- line5', 'line6')],
                         list(csplit(lines, r'----')))

        # string case: empty first buffer
        self.assertEqual([('---- line2', 'line3', 'line4'), ('---- line5', 'line6')],
                         list(csplit(lines[1:], r'----')))

        # regex case
        self.assertEqual([('line1', '---- line2'), ('line3', 'line4', '---- line5'), ('line6',)],
                         list(csplit(lines, re.compile(r'line[36].*'))))

    def test_ensure_text(self):
        self.assertEqual(None, ensure_text(None))
        self.assertEqual(u'', ensure_text(b''))
        self.assertEqual(u'', ensure_text(u''))
        self.assertEqual(u'abc', ensure_text(b'abc'))
        self.assertEqual(u'abc', ensure_text(u'abc'))
        with self.assertRaises(AssertionError):
            ensure_text([])
