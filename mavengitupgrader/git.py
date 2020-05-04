"""
Branch (represents the Git branch that the update will be contained in)
"""

import subprocess
import os.path


class Branch:
    def __init__(self, name: str, based_on: str,
                 _git_dir_to_make: str = None, _pom_filename_to_copy: str = None):
        self.name = name
        self.based_on = based_on
        self._git_directory = _git_dir_to_make
        if self._git_directory:
            if not os.path.isdir(self._git_directory):
                subprocess.run(['mkdir', self._git_directory], check=True)
            if not os.path.isdir(self._git_directory + "/.git"):
                subprocess.run(['git', 'init'], check=True,
                               cwd=self._git_directory)
            if _pom_filename_to_copy:
                subprocess.run(['cp', _pom_filename_to_copy,
                                self._git_directory + "/"], check=True)
                subprocess.run(['git', 'add', _pom_filename_to_copy],
                               check=True, cwd=self._git_directory)
                subprocess.run(['git', 'config', 'user.email',
                                "garrettheath4@github.com"],
                               cwd=self._git_directory)
                subprocess.run(['git', 'config', 'user.name',
                                "Garrett Koller"], cwd=self._git_directory)
                subprocess.run(['git', 'commit', '-m', "Unit test commit"],
                               check=True, cwd=self._git_directory)

    def activate(self):
        # equivalent to `git branch --show-current` but works in older versions
        current_branch_proc = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stdout=subprocess.PIPE, check=True, cwd=self._git_directory)
        current_branch_str = current_branch_proc.stdout.decode('utf-8')
        if current_branch_str != self.name:
            subprocess.run(['git', 'update-index', '--refresh'],
                           cwd=self._git_directory)
            subprocess.run(['git', 'diff-index', '--quiet', 'HEAD', '--'],
                           check=True, cwd=self._git_directory)
            subprocess.run(['git', 'checkout', self.based_on],
                           check=True, cwd=self._git_directory)
            subprocess.run(['git', 'checkout', '-b', self.name],
                           check=True, cwd=self._git_directory)
