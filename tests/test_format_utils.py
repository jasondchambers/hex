"""Tests for format.py."""
import unittest
from netorg_core import format_utils

# pylint: disable=line-too-long
# pylint: disable=missing-function-docstring

list_of_strings = [
    'Jasons watch',
    'Jasons laptop',
    'SONOS Bedroom speaker',
    'SONOS Hifi speaker',
    'SONOS Kitchen',
    'Smart switch 1',
    'Very very very very very very long string',
    'Roses watch',
    'Roses phone',
    'Webcam backyard',
    'Webcam garage'
]


class TestFormatUtils(unittest.TestCase):
    """Tests for format_utils."""

    def test_columnize_1(self):
        test1 = [
            ' J...',
            ' J...',
            ' S...',
            ' S...',
            ' S...',
            ' S...',
            ' V...',
            ' R...',
            ' R...',
            ' W...',
            ' W...'
        ]
        rows = format_utils.convert_to_list(
            format_utils.columnize(list_of_strings, left_margin_width=1, number_of_columns=1, column_width=4))
        self.assertEqual(rows, test1)

    def test_columnize_2(self):
        test2 = [
            '   Jasons watch                            Jasons laptop                          ',
            '   SONOS Bedroom speaker                   SONOS Hifi speaker                     ',
            '   SONOS Kitchen                           Smart switch 1                         ',
            '   Very very very very very very long s... Roses watch                            ',
            '   Roses phone                             Webcam backyard                        ',
            '   Webcam garage                           '
        ]
        rows = format_utils.convert_to_list(
            format_utils.columnize(list_of_strings, left_margin_width=3, number_of_columns=2, column_width=39))
        self.assertEqual(rows, test2)

    def test_columnize_3(self):
        test3 = [
            '  Jasons watch    Jasons laptop   SONOS Bedroo... SONOS Hifi s... SONOS Kitchen  ',
            '  Smart switch 1  Very very ve... Roses watch     Roses phone     Webcam backyard',
            '  Webcam garage      '
        ]
        rows = format_utils.convert_to_list(
            format_utils.columnize(list_of_strings, left_margin_width=2, number_of_columns=5, column_width=15))
        self.assertEqual(rows, test3)

    def test_columnize_4(self):
        test4 = [
            'Jasons watch    Jasons laptop   SONOS Bedroo... SONOS Hifi s... SONOS Kitchen   Smart switch 1 ',
            'Very very ve... Roses watch     Roses phone     Webcam backyard Webcam garage   '
        ]
        rows = format_utils.convert_to_list(
            format_utils.columnize(list_of_strings, left_margin_width=-99, number_of_columns=6, column_width=15))
        self.assertEqual(rows, test4)

    def test_columnize_5(self):
        test5 = [
            '      Jasons ... Jasons ... SONOS B... SONOS H... SONOS K... Smart s... Very ve...',
            '      Roses w... Roses p... Webcam ... Webcam ...   '
        ]
        rows = format_utils.convert_to_list(
            format_utils.columnize(list_of_strings, left_margin_width=6, number_of_columns=7, column_width=10))
        self.assertEqual(rows, test5)

    def test_columnize_6(self):
        test6 = [
            'J...',
            'J...',
            'S...',
            'S...',
            'S...',
            'S...',
            'V...',
            'R...',
            'R...',
            'W...',
            'W...'
        ]
        rows = format_utils.convert_to_list(
            format_utils.columnize(list_of_strings, left_margin_width=0, number_of_columns=1, column_width=4))
        self.assertEqual(rows, test6)

    def test_columnize_7(self):
        test7 = [
            'Jas',
            'Jas',
            'SON',
            'SON',
            'SON',
            'Sma',
            'Ver',
            'Ros',
            'Ros',
            'Web',
            'Web'
        ]
        rows = format_utils.convert_to_list(
            format_utils.columnize(list_of_strings, left_margin_width=0, number_of_columns=1, column_width=3))
        self.assertEqual(rows, test7)

    def test_columnize_8(self):
        test8 = [
            'Ja',
            'Ja',
            'SO',
            'SO',
            'SO',
            'Sm',
            'Ve',
            'Ro',
            'Ro',
            'We',
            'We'
        ]
        rows = format_utils.convert_to_list(
            format_utils.columnize(list_of_strings, left_margin_width=0, number_of_columns=1, column_width=2))
        self.assertEqual(rows, test8)

    def test_columnize_9(self):
        test9 = [
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            ''
        ]
        rows = format_utils.convert_to_list(
            format_utils.columnize(list_of_strings, left_margin_width=0, number_of_columns=1, column_width=0))
        self.assertEqual(rows, test9)

    def test_columnize_10(self):
        test10 = [
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            ''
        ]
        rows = format_utils.convert_to_list(
            format_utils.columnize(list_of_strings, left_margin_width=0, number_of_columns=1, column_width=-1))
        self.assertEqual(rows, test10)
