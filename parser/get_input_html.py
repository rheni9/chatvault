"""
Utility module for locating the input HTML file containing exported chat data.
"""

import os
import sys
import glob

WARNING_SIGN = "\u26A0\uFE0F"


def get_input_html_path() -> str:
    """
    Determine the path to the input HTML file for chat export.

    Priority:
        1. If a filename is passed as a command-line argument, verify that it
           exists in the ``data/html/`` directory and has a .html extension.
        2. If no filename is provided, automatically scan the ``data/html/``
           directory for .html files.
        3. If multiple HTML files are found, prompt the user to select one
           interactively.

    :returns: Full path to the HTML file
    :rtype: str
    :raises SystemExit: If the input is invalid, file not found,
                        or user cancels
    """
    html_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "html")
    )

    # Check command-line arguments
    if len(sys.argv) > 2:
        print(f"{WARNING_SIGN}  Too many arguments. "
              "Provide only one filename or none.")
        raise SystemExit(1)

    if len(sys.argv) == 2:
        filename = sys.argv[1]
        full_path = os.path.join(html_dir, filename)

        if not os.path.isfile(full_path):
            print(f"{WARNING_SIGN}  File '{filename}' not found in {html_dir}")
            raise SystemExit(1)

        if not filename.lower().endswith(".html"):
            print(f"{WARNING_SIGN}  File '{filename}' is not an HTML file.")
            raise SystemExit(1)

        return full_path

    # Auto-detect .html files
    html_files = sorted(
        f for f in glob.glob(os.path.join(html_dir, "*.html"))
        if os.path.isfile(f)
    )

    if not html_files:
        print(f"{WARNING_SIGN}  No HTML files found in data/html/")
        raise SystemExit(1)

    if len(html_files) == 1:
        return html_files[0]

    # Multiple files - prompt user
    print("\u2139   Multiple HTML files found:\n")
    for i, path in enumerate(html_files, 1):
        print(f"  {i}. {os.path.basename(path)}")

    while True:
        choice = input(
            "Enter the number of the file to use "
            "(or press Enter to cancel): "
        ).strip()

        if not choice:
            print("Cancelled by user.")
            raise SystemExit(0)

        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(html_files):
                return html_files[index - 1]

        print(f"{WARNING_SIGN}  Invalid selection. Please try again.")
