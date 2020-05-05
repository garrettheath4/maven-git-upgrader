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
import os
import re
from typing import Callable, Tuple, Optional

from mavengitupgrader.git import Branch
from mavengitupgrader.maven import Pom, Dependency


class Update:
    update_line_matcher = re.compile(
        r' {3}([a-zA-Z0-9.]+):([a-zA-Z0-9-_.]+) \.*(\n\[INFO\] *)? ([0-9.]+) -> '
        r'([0-9.]+)'
    )

    def __init__(self, update_line: str = None, group: str = None,
                 artifact: str = None, current_version: str = None,
                 latest_version: str = None,
                 source_branch: str = None,
                 pom_path: str = "pom.xml", _git_dir_to_make: str = None,
                 _pom_filename_to_copy: str = None):
        if not update_line and \
                not (group and artifact and current_version and latest_version):
            raise ValueError("Either update_line or one of the following were"
                             "not supplied: group, artifact, current_version, "
                             "or latest_version")
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
        self.pom_dependency: Optional[Dependency] = None
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
        # _read_pom() must be after Branch creates mock repo
        self._read_pom(expected_current_version=current_version)

    def apply(self, switch_to_source_branch_afterwards: bool = True,
              push: bool = False):
        if not self.parsed:
            raise RuntimeError("Unable to apply Update because the provided"
                               " update line was unable to be parsed: "
                               + str(self.update_line))
        if not self.pom_dependency:
            raise RuntimeError("Unable to locate POM dependency the given"
                               " update line refers to: "
                               + str(self.update_line))
        is_new_branch = self.target_branch.activate()
        if not is_new_branch:
            # determine if existing branch already has this update
            self._read_pom()
        if self.pom_dependency.get_version() != self.latest_version:
            self.pom_dependency.set_version(self.latest_version)
            self._pom.save(self._pom_path)
            self.target_branch.commit(f"Updating dependency {str(self)}",
                                      os.path.basename(self._pom_path))
            if push:
                self.target_branch.push()
        else:
            logging.info("An existing branch appears to already have this "
                         "update. Skipping %s", str(self))
        if switch_to_source_branch_afterwards:
            self.target_branch.prepare()

    def __str__(self):
        if self.parsed:
            return f"{self.group}:{self.artifact} " \
                   f"{self.current_version} -> {self.latest_version}"
        else:
            return self.update_line

    def _read_pom(self, expected_current_version: str = None):
        self._pom = Pom(self._pom_path)  # must be after Branch creates mock repo
        if expected_current_version:
            self.pom_dependency = self._pom.get_dependency(
                artifact_id=self.artifact, group_id=self.group,
                version=expected_current_version
            )
        else:
            self.pom_dependency = self._pom.get_dependency(
                artifact_id=self.artifact, group_id=self.group
            )


def update_from_matches_tuple(matches: tuple,
                              source_branch: str = None) -> Update:
    (group, artifact, _, current_version, latest_version) = matches
    return Update(group=group, artifact=artifact,
                  current_version=current_version,
                  latest_version=latest_version, source_branch=source_branch)


def update_from_matches_tuple_using_source_branch_fn(
        source_branch: str = None) -> Callable[[Tuple], Update]:
    return lambda matches: update_from_matches_tuple(matches, source_branch)
