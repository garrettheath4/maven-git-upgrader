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
import logging
import re

from mavengitupgrader.git import Branch
from mavengitupgrader.maven import Pom


class Update:
    update_line_matcher = re.compile(
        r' {3}([a-z0-9.]+):([a-z0-9-_.]+) \.*(\n\[INFO\] *)? ([0-9.]+) -> '
        r'([0-9.]+)'
    )

    def __init__(self, update_line: str = None, group: str = None,
                 artifact: str = None, current_version: str = None,
                 latest_version: str = None,
                 source_branch: str = "master",
                 pom_path: str = "pom.xml", _git_dir_to_make: str = None,
                 _pom_filename_to_copy: str = None):
        self.update_line = update_line
        self.source_branch = source_branch
        self._pom_path = pom_path
        self.parsed = False
        self._pom = None
        self.group = group
        self.artifact = artifact
        self.current_version = current_version
        self.latest_version = latest_version
        self.target_branch = None
        self.pom_dependency = None
        if not update_line and \
                not (group and artifact and current_version and latest_version):
            raise ValueError("Either update_line or one of the following were"
                             "not supplied: group, artifact, current_version, "
                             "or latest_version")
        """
        [INFO]   io.github.classgraph:classgraph ..................... 4.8.71 -> 4.8.78
        [INFO]   com.fasterxml.jackson.module:jackson-module-scala_2.11 ...
        [INFO]                                                         2.10.3 -> 2.11.0
        """
        if group and artifact and current_version and latest_version:
            self.parsed = True
        else:
            matches = re.findall(Update.update_line_matcher, update_line)
            if matches and len(matches) == 1:
                logging.debug("matches[0] = %s", str(matches[0]))
                (group, artifact, _, current_version, latest_version) = matches[0]
                self.parsed = True
                self.group = group
                self.artifact = artifact
                self.current_version = current_version
                self.latest_version = latest_version
            else:
                if not matches or len(matches) == 0:
                    raise ValueError("No match found")
                else:
                    raise ValueError(f"Too many matches found: {matches}")
        self.target_branch = Branch(f"update-{artifact}", source_branch,
                                    _git_dir_to_make=_git_dir_to_make,
                                    _pom_filename_to_copy=_pom_filename_to_copy)
        self._pom = Pom(self._pom_path)  # must be after Branch creates repo
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
        self.target_branch.activate()
        self.pom_dependency.set_version(self.latest_version)
        self._pom.save(self._pom_path)

    def __str__(self):
        if self.parsed:
            return f"{self.group}:{self.artifact} {self.current_version} -> {self.latest_version}"
        else:
            return self.update_line


def update_from_matches_tuple(matches: tuple) -> Update:
    (group, artifact, _, current_version, latest_version) = matches
    return Update(group=group, artifact=artifact,
                  current_version=current_version,
                  latest_version=latest_version)
