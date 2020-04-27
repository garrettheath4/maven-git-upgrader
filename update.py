"""
Update: represents a single Maven dependency that needs to be updated

Update (in this module)
|
+-> Branch (represents the Git branch that the update will be contained in)
|
+-> Pom (represents the Maven pom.xml file that needs to be modified)
    |
    +-> Dependency (represents a single dependency element in the Pom xml)
"""

import re

from git import Branch
from maven import Pom


class Update:
    def __init__(self, update_line: str, pom_filename: str = "pom.xml", ):
        self.parsed = False
        self.update_line = update_line
        if not update_line:
            return
        matches = re.findall(
            r' {3}([a-z0-9.]+):([a-z0-9-]+) \.* ([0-9.]+) -> ([0-9.]+)',
            update_line)
        if matches and len(matches) == 1:
            (group, artifact, current_version, latest_version) = matches[0]
            self.parsed = True
            self.group = group
            self.artifact = artifact
            self.current = current_version
            self.latest = latest_version
            self.branch = Branch(f"update-{artifact}")
            self.pom = Pom(pom_filename)
            self.pom_dependency = self.pom.get_dependency(
                artifact_id=artifact, group_id=group, version=current_version)

    def __str__(self):
        if self.parsed:
            return f"{self.group}:{self.artifact} {self.current} -> {self.latest}"
        else:
            return self.update_line
