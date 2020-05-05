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

import argparse
import logging
import os
import sys

from mavengitupgrader.git import get_current_branch_name
from mavengitupgrader.upgrader import calculate_updates, apply_updates


def main():
    logging.debug("Python version " + sys.version.split('\n')[0])
    args = parse_args()
    git_directory = args.directory
    if not git_directory:
        if wrong_current_directory():
            raise RuntimeError("Switch to a different directory before running "
                               "this module with `python3 -m mavengitupgrader`")
        logging.info("Upgrading Maven project in Git repo in current directory")
    git_source_branch = args.source_branch
    if not git_source_branch:
        git_source_branch = get_current_branch_name(git_repo_path=git_directory)
    updates = calculate_updates(git_directory=git_directory,
                                git_source_branch=git_source_branch)
    print(f"Maven found {len(updates)} available dependency updates:")
    for update in updates:
        print("  " + str(update))
    if args.yes:
        response = "yes"
    else:
        response = input(f"Apply the above updates to the '{git_source_branch}' "
                         f"branch? (yes/no) [default: yes]: ")
    if not response or (response and response.lower()[0] != 'n'):
        logging.info("Applying %d updates...", len(updates))
        apply_updates(updates, push=args.push)
    else:
        logging.info("Exiting.")


def parse_args():
    description = "Checks for updates to dependencies in a Maven project and " \
                  "creates a Git branch for each update for isolated testing " \
                  "and easy integration."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-d', '--directory', type=str, default=None,
                        help="The path to the directory containing a Git "
                             "repository for a valid Maven project (default: "
                             "current directory)")
    parser.add_argument('-b', '--source-branch', type=str, default=None,
                        help="The Git branch in the repository to base updates "
                             "on (default: current branch)")
    parser.add_argument('-y', '--yes', default=False, action='store_true',
                        help="Skip any normal (non-error) interactive prompts "
                             "and continue as if they were answered with the "
                             "default/yes option")
    parser.add_argument('-p', '--push', default=False, action='store_true',
                        help="Automatically push new branches to the remote "
                             "'origin'")
    return parser.parse_args()


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
    main()
