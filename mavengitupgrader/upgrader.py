#!/usr/bin/env python3

"""
maven-git-updater

Checks for updates to Maven dependencies in a project and creates git branches
for each update to allow for isolated unit testing and easy integration.

upgrader.py (the main script; this script)
|
+-> Update (represents a single Maven dependency that needs to be updated)
    |
    +-> Branch (represents the Git branch that the update will be contained in)
    |
    +-> Pom (represents the Maven pom.xml file that needs to be modified)
        |
        +-> Dependency (represents a single dependency element in the Pom xml)
"""

import logging
import re
import subprocess
from typing import List

from mavengitupgrader.update import (
    Update,
    update_from_matches_tuple_using_source_branch_fn
)


def stdout_to_update_list(maven_stdout: str, source_branch: str = None) -> \
        List[Update]:
    matches = re.findall(Update.update_line_matcher, maven_stdout)
    logging.debug("Parsed %d available updates from Maven output", len(matches))
    return list(map(
        update_from_matches_tuple_using_source_branch_fn(source_branch), matches
    ))


def calculate_updates(git_directory: str = None,
                      git_source_branch: str = None) -> List[Update]:
    """
    Runs `mvn versions:display-dependency-updates` and parses the output to
    return a list of Update objects representing the Maven project's
    available upgrades for its dependencies.

    Looking for:
    [INFO] The following dependencies in Dependencies have newer versions:
    [INFO]   io.github.classgraph:classgraph ..................... 4.8.71 -> 4.8.75
    [INFO]   us.catalist.fusion:fusion-core ........................ 6.3.3 -> 6.3.4
    [INFO]   us.catalist.fusion:fusion-injection-hk2 ............... 6.3.3 -> 6.3.4
    [INFO]   us.catalist.fusion:fusion-jobs ........................ 6.3.3 -> 6.3.4
    [INFO]   us.catalist.fusion:fusion-logic ....................... 6.3.3 -> 6.3.4
    [INFO]   us.catalist.fusion:fusion-persistence ................. 6.3.3 -> 6.3.4
    [INFO]   us.catalist.fusion:fusion-workflow .................... 6.3.3 -> 6.3.4

    :return: List of Update objects
    """
    logging.info("Maven is checking for updates...")
    display_updates = subprocess.run(
        ['mvn', 'versions:display-dependency-updates'], stdout=subprocess.PIPE,
        cwd=git_directory)
    stdout = display_updates.stdout.decode('utf-8')
    if display_updates.returncode:
        logging.error(stdout)
        display_updates.check_returncode()
    logging.info("Maven done. Processing updates...")
    return stdout_to_update_list(maven_stdout=stdout,
                                 source_branch=git_source_branch)


def apply_updates(updates: List[Update], push: bool = False):
    for u in updates:
        u.apply(push=push)
    logging.info("Applied updates to %d new branches.", len(updates))
    if not push:
        logging.info("Remember to test and then push these branches.")


def calculate_and_apply_updates(git_directory: str = None,
                                git_source_branch: str = None):
    updates = calculate_updates(git_directory=git_directory,
                                git_source_branch=git_source_branch)
    apply_updates(updates)
