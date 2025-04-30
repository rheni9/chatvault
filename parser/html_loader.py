"""
Provides functionality to load and parse an input HTML file containing
chat export data. Wraps BeautifulSoup for consistent parsing and error
handling.
"""

import os
from bs4 import BeautifulSoup


def load_html(path: str) -> BeautifulSoup:
    """
    Load and parse an HTML file into a BeautifulSoup object.

    :param path: Path to the HTML file
    :type path: str
    :return: Parsed HTML as BeautifulSoup object
    :rtype: bs4.BeautifulSoup
    :raises FileNotFoundError: If the file does not exist
    :raises ValueError: If the file extension is not .html or .htm
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    if not path.lower().endswith((".html", ".htm")):
        raise ValueError(f"Not an HTML file: {path}")

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "lxml")
    return soup
