import subprocess


class Branch:
    def __init__(self, name: str):
        self.name = name

    def switch_to(self):
        # equivalent to `git branch --show-current` but works in older versions
        current_branch_proc = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stdout=subprocess.PIPE, check=True)
        current_branch_str = current_branch_proc.stdout.decode('utf-8')
        if current_branch_str != self.name:
            subprocess.run(['git', 'checkout', '-b', self.name], check=True)
