"""
Branch (represents the Git branch that the update will be contained in)
"""
import logging
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

    def prepare(self):
        # equivalent to `git branch --show-current` but works in older versions
        current_branch_proc = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stdout=subprocess.PIPE, check=True, cwd=self._git_directory)
        current_branch_str = current_branch_proc.stdout.decode('utf-8')
        logging.debug("Current branch: %s", current_branch_str)
        if current_branch_str != self.name:
            subprocess.run(['git', 'update-index', '--refresh'],
                           cwd=self._git_directory)
            diff_proc = subprocess.run(
                ['git', 'diff-index', '--quiet', 'HEAD', '--'],
                cwd=self._git_directory)
            if diff_proc.returncode:
                logging.error(diff_proc.stdout)
                logging.error("Git directory is not clean")
                diff_proc.check_returncode()
            subprocess.run(['git', 'checkout', self.based_on],
                           check=True, cwd=self._git_directory)

    def activate(self) -> bool:
        """
        Check out the branch represented by this Branch object.

        :raises: CalledProcessError if a git command encounters an error.

        :return: True if a new branch was created or False if a pre-existing
                 branch gets checked out
        """
        self.prepare()
        local_exists: bool = subprocess.run(
            ['git', 'rev-parse', '--verify', self.name],
            cwd=self._git_directory
        ).returncode == 0
        remote_exists: bool = subprocess.run(
            ['git', 'ls-remote', '--exit-code', '--heads', 'origin', self.name],
            cwd=self._git_directory
        ).returncode == 0
        if local_exists or remote_exists:
            logging.info("Checking out existing %s branch %s",
                         "local" if local_exists else "remote", self.name)
            subprocess.run(['git', 'checkout', self.name],
                           check=True, cwd=self._git_directory)
            return False
        else:
            logging.info("Creating new branch %s based on %s",
                         self.name, self.based_on)
            subprocess.run(['git', 'checkout', '-b', self.name],
                           check=True, cwd=self._git_directory)
            return True

    def commit(self, message: str, pom_file: str = "pom.xml"):
        subprocess.run(['git', 'add', pom_file],
                       check=True, cwd=self._git_directory)
        subprocess.run(['git', 'commit', '-m', message],
                       check=True, cwd=self._git_directory)
