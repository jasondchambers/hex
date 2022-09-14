"""Text formatting utilities for producing columnar output."""
from itertools import zip_longest
import shutil
from typing import List


def shorten_string(a_string: str, width: int, placeholder: str) -> str:
    """
    Take something like this
    'Hello there Jason'
    and return
    'Hello the...'
    """
    if len(a_string) <= width:
        return a_string
    if width <= 0:
        return ''
    if len(placeholder) >= width:
        return a_string[:width]
    nchars = width - len(placeholder)
    return a_string[:nchars]+placeholder


def pad_string(a_string: str, width: int) -> str:
    """
    Take something like this
    'Hello'
    and return it padded
    'Hello       '
    """
    return "{: <{width}}".format(a_string, width=width)


def process_string(a_string: str, width: int, placeholder: str) -> str:
    """Shorten and pad a string."""
    width = max(width, 0)
    if width <= 0:
        return ''
    a_string = shorten_string(a_string, width, placeholder)
    a_string = pad_string(a_string, width)
    return a_string


def process_strings(list_of_string: List[str], width: int, placeholder: str) -> List[str]:
    return [process_string(s, width, "...") for s in list_of_string]


def shift_string(a_string: str, left_margin_width: int, column_number: int, number_of_columns: int) -> str:
    if column_number % number_of_columns == 0:
        return (" " * left_margin_width) + a_string
    return a_string


def apply_left_margin(list_of_string: List[str], left_margin_width: int, number_of_columns: int) -> List[str]:
    if left_margin_width <= 0:
        return list_of_string
    return [shift_string(s, left_margin_width, idx, number_of_columns) for idx, s in enumerate(list_of_string)]


def blockwise(some_list, size=2, fillvalue=None) -> zip_longest:
    """Combine individual items in a list into tuples."""
    list_iterator = iter(some_list)
    return zip_longest(*[list_iterator]*size, fillvalue=fillvalue)


def columnize(list_of_strings: List[str], left_margin_width: int, number_of_columns: int, column_width: int) -> zip_longest:
    """
    Take a flat list of strings and organize them into formatted rows.
    Useful for creating multi-column console output to reduce need for
    scrolling by the user.
    """
    column_width = max(column_width, 0)
    list_of_strings = process_strings(
        list_of_strings, width=column_width, placeholder="...")
    list_of_strings = apply_left_margin(
        list_of_strings, left_margin_width, number_of_columns)
    rows = blockwise(list_of_strings, number_of_columns, fillvalue='')
    return rows


def adaptive_columnize(list_of_strings: List[str], left_margin_width: int) -> zip_longest:
    """
    Take into consideration the teminal width to determine how
    to columnize.
    """
    terminal_width = shutil.get_terminal_size((80, 20))[0]
    min_ideal_column_width = 20
    num_columns = int(terminal_width / (min_ideal_column_width + 1))
    num_columns = max(num_columns, 1)
    column_width = min(terminal_width, min_ideal_column_width)
    return columnize(list_of_strings, left_margin_width, num_columns, column_width)


def convert_to_list(rows: zip_longest) -> List[str]:
    """Convert zip_longest to simple list."""
    return_list = []
    for row in rows:
        return_list.append(' '.join(row))
    return return_list
