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
    def __init__(self, update_line: str, branch_to_update_from: str = "master",
                 pom_filename: str = "pom.xml", _git_dir_to_make: str = None,
                 _pom_filename_to_copy: str = None):
        self.update_line = update_line
        self.branch_to_update_from = branch_to_update_from
        self._pom_filename = pom_filename
        self.parsed = False
        self._pom = Pom(self._pom_filename)
        self.group = None
        self.artifact = None
        self.current = None
        self.latest = None
        self.branch = None
        self.pom_dependency = None
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
            self.branch = Branch(f"update-{artifact}", branch_to_update_from,
                                 _git_dir_to_make=_git_dir_to_make,
                                 _pom_filename_to_copy=_pom_filename_to_copy)
            self.pom_dependency = self._pom.get_dependency(
                artifact_id=artifact, group_id=group, version=current_version)

    def apply(self):
        if not self.parsed:
            raise RuntimeError("Unable to apply Update because the provided"
                               " update line was unable to be parsed: "
                               + str(self.update_line))
        if not self.pom_dependency:
            raise RuntimeError("Unable to locate POM dependency the given"
                               " update line refers to: "
                               + str(self.update_line))
        self.branch.activate()
        self.pom_dependency.set_version(self.latest)
        self._pom.save(self._pom_filename)

    def __str__(self):
        if self.parsed:
            return f"{self.group}:{self.artifact} {self.current} -> {self.latest}"
        else:
            return self.update_line
