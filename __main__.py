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
import sys

from upgrader import calculate_updates

if __name__ == "__main__":
    logging.debug("Python version " + sys.version.split('\n')[0])
    git_directory = None
    if len(sys.argv) == 2:
        git_directory = sys.argv[1]
    updates = calculate_updates(git_directory=git_directory)
    for u in updates:
        print(u)
