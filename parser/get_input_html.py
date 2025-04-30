"""
Utility module for locating the input HTML file containing exported chat data.
"""

import os
import sys
import glob


def get_input_html_path() -> str:
    """
    Determine the path to an input HTML file.

    If a filename is passed as a command-line argument, check that the file
    exists in the expected directory and has an HTML extension. If no argument
    is given, try to detect a single HTML file in the data/html/ directory.

    :return: Full path to the HTML file
    :rtype: str
    :raises FileNotFoundError: If the file does not exist
    :raises ValueError: If the file is not an HTML file
    :raises RuntimeError: If multiple HTML files are found
    """

    # Directory containing HTML input files
    html_dir = os.path.join(os.path.dirname(__file__), "..", "data", "html")

    # If filename is passed as an argument
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        full_path = os.path.join(html_dir, filename)

        if not os.path.isfile(full_path):
            raise FileNotFoundError(
                f"File '{filename}' does not exist in {html_dir}"
            )

        if not filename.lower().endswith(".html"):
            raise ValueError(f"File '{filename}' is not an HTML file.")

        return full_path

    # Auto-detect HTML files in the directory
    html_files = glob.glob(os.path.join(html_dir, "*.html"))

    if len(html_files) == 1:
        return html_files[0]
    elif not html_files:
        raise FileNotFoundError("No HTML files found in data/html/")
    else:
        files_list = "\n".join(f"- {os.path.basename(f)}" for f in html_files)
        raise RuntimeError(
            f"Multiple HTML files found in {html_dir}. "
            f"Please specify one of the following:\n{files_list}"
        )
