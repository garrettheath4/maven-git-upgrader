import re


class Update:
    def __init__(self, update_line):
        self.update_line = update_line
        matches = re.findall(
            r' {3}([a-z0-9.]+):([a-z0-9-]+) \.* ([0-9.]+) -> ([0-9.]+)',
            update_line)
        if matches and len(matches) == 1:
            (group, artifact, current_version, latest_version) = matches[0]
            self.group = group
            self.artifact = artifact
            self.current = current_version
            self.latest = latest_version

    def __str__(self):
        if self.group:
            return f"{self.group}:{self.artifact} {self.current} -> {self.latest}"
        else:
            return self.update_line


