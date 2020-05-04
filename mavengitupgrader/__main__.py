#!/usr/bin/env python3

"""
Checks for updates to dependencies in a Maven project and creates a Git
branch for each update for isolated testing and easy integration.
"""

__author__ = "Garrett Heath Koller"
__copyright__ = "Copyright 2020, Garrett Heath Koller"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Garrett Heath Koller"
__email__ = "garrettheath4@gmail.com"
__status__ = "Prototype"

import logging
import os
import sys

from mavengitupgrader.upgrader import calculate_updates


def wrong_current_directory() -> bool:
    bad_dirs = ("mavengitupgrader", "maven-git-upgrader")
    current_path = os.getcwd()
    current_dir = os.path.basename(current_path)
    if current_dir in bad_dirs:
        return True
    parent_path = os.path.dirname(current_path)
    parent_dir = os.path.basename(parent_path)
    if parent_dir in bad_dirs:
        return True
    return False


if __name__ == "__main__":
    logging.debug("Python version " + sys.version.split('\n')[0])
    logging.debug(f"__file__ = {__file__}")
    git_directory = None
    if len(sys.argv) == 2:
        git_directory = sys.argv[1]
    if not git_directory and wrong_current_directory():
        raise RuntimeError("Switch to a different directory before running "
                           "this module with `python -m mavengitupgrader`")
    updates = calculate_updates(git_directory=git_directory)
    for u in updates:
        print(u)
