"""
HTML path locator for Telegram exports (Arcanum App).

Determines which HTML file should be loaded for parsing, supporting
command-line filename input or interactive selection.
"""

import os
import sys
import glob
import logging

logger = logging.getLogger(__name__)
WARNING_SIGN = "\u26A0\uFE0F"


def get_input_html_path() -> str:
    """
    Determine the path to the input HTML file for chat export.

    Priority:
        1. Use filename passed as command-line argument (validate).
        2. If none provided, scan `data/html/` for HTML files.
        3. If multiple found, prompt user to choose one.

    :return: Absolute path to selected HTML file.
    :raises SystemExit: On invalid input, not found, or cancellation.
    """
    html_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "html")
    )

    args = sys.argv[1:]
    if len(args) > 1:
        logger.warning("[INPUT|HTML] Too many command-line arguments: %s", args)
        raise SystemExit(f"{WARNING_SIGN}  Too many arguments. Provide one filename or none.")

    # === Use argument if given ===
    if args:
        filename = args[0]
        full_path = os.path.join(html_dir, filename)

        if not os.path.isfile(full_path):
            logger.warning("[INPUT|HTML] File not found: %s", full_path)
            raise SystemExit(f"{WARNING_SIGN}  File '{filename}' not found in {html_dir}")

        if not filename.lower().endswith(".html"):
            logger.warning("[INPUT|HTML] Invalid extension: %s", filename)
            raise SystemExit(f"{WARNING_SIGN}  File '{filename}' is not an HTML file.")

        logger.info("[INPUT|HTML] Using file from argument: %s", filename)
        return full_path

    # === Auto-detect .html files ===
    html_files = sorted(
        f for f in glob.glob(os.path.join(html_dir, "*.html"))
        if os.path.isfile(f)
    )

    if not html_files:
        logger.warning("[INPUT|HTML] No HTML files found in %s", html_dir)
        raise SystemExit(f"{WARNING_SIGN}  No HTML files found in data/html/")

    if len(html_files) == 1:
        logger.info("[INPUT|HTML] Single file found: %s", html_files[0])
        return html_files[0]

    # === Interactive selection ===
    print("\u2139  Multiple HTML files found:\n")
    for i, path in enumerate(html_files, 1):
        print(f"  {i}. {os.path.basename(path)}")

    while True:
        choice = input("\nEnter the number of the file to use "
                       "(or press Enter to cancel): ").strip()

        if not choice:
            logger.info("[INPUT|HTML] Selection cancelled by user.")
            raise SystemExit("Cancelled by user.")

        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(html_files):
                logger.info("[INPUT|HTML] User selected: %s", html_files[index - 1])
                return html_files[index - 1]

        print(f"{WARNING_SIGN}  Invalid selection. Please try again.")
