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

import sys
import subprocess
import logging
from typing import List

from update import Update


logging.basicConfig(level="DEBUG")
log = logging.getLogger("upgrader")


def main():
    log.debug("Python version " + sys.version.split('\n')[0])
    updates = calculate_updates()
    for u in updates:
        print(u)


def calculate_updates() -> List[Update]:
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
    log.info("Maven is checking for updates...")
    display_updates = subprocess.run(
        ['mvn', 'versions:display-dependency-updates'],
        stdout=subprocess.PIPE, check=True)
    log.info("Maven done. Processing updates...")
    stdout = display_updates.stdout.decode('utf-8')
    lines = stdout.split('\n')
    upgrade_lines = filter(lambda l: l.startswith("[INFO] ") and " -> " in l,
                           lines)
    return list(map(Update, upgrade_lines))


if __name__ == "__main__":
    main()
