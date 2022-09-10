"""Text formatting utilities for producing columnar output."""
from itertools import zip_longest
import shutil
from typing import List

def shorten_string(a_string: str, max_width: int, placeholder: str) -> str:
    """
    Take something like this
    'Hello there Jason'
    and return
    'Hello the...'
    """
    if len(a_string) <= max_width:
        return a_string
    if max_width <= 0:
        return ''
    if len(placeholder) >= max_width:
        return a_string[:max_width]
    nchars = max_width - len(placeholder)
    return a_string[:nchars]+placeholder

def shorten_strings(list_of_string: List[str], width: int, placeholder: str) -> List[str]:
    """Shorten a list of strings to the specified width.  """
    width = max(width,0)
    if width <= 0:
        return [''] * len(list_of_string)
    return [shorten_string(long_string, width, placeholder) for long_string in list_of_string]

def pad_strings(list_of_string: List[str], column_width: int) -> List[str]:
    """Pad a list of strings with spaces to ensure they are the same width."""
    return ["{: <{width}}".format(s, width=column_width) for s in list_of_string]

def blockwise(some_list, size=2, fillvalue=None) -> zip_longest:
    """Combine individual items in a list into tuples."""
    list_iterator = iter(some_list)
    return zip_longest(*[list_iterator]*size, fillvalue=fillvalue)

def columnize(list_of_strings: List[str], number_of_columns: int, column_width: int) -> zip_longest:
    """
    Take a flat list of strings and organize them into formatted rows.
    Useful for creating multi-column console output to reduce need for
    scrolling by the user.
    """
    column_width = max(column_width,0)
    list_of_strings = shorten_strings(list_of_strings, width=column_width, placeholder="...")
    list_of_strings = pad_strings(list_of_strings, column_width=column_width)
    rows = blockwise(list_of_strings, number_of_columns, fillvalue='')
    return rows

def adaptive_columnize(list_of_strings: List[str])  -> zip_longest:
    """
    Take into consideration the teminal width to determine how
    to columnize.
    """
    terminal_width = shutil.get_terminal_size((80, 20))[0]
    min_ideal_column_width = 20
    num_columns = int(terminal_width / (min_ideal_column_width + 1))
    num_columns = max(num_columns,1)
    column_width = min(terminal_width, min_ideal_column_width)
    return columnize(list_of_strings,num_columns, column_width)

def convert_to_list(rows: zip_longest) -> List[str]:
    """Convert zip_longest to simple list."""
    return_list = []
    for row in rows:
        return_list.append(' '.join(row))
    return return_list
