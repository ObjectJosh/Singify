
import subprocess as sp
import re

def say(text: str) -> None:
    sp.call(['say', text])

def simplify_string(string):
    """ Removes punctuation and capitalization from given string
    Args:
        string(string): string to be simplified
    Returns:
        string: a string without punctuation or capitalization
    """
    return re.sub(r'[^a-zA-Z0-9]', '', string).lower()