# Maven Git Upgrader

*Maven Git Upgrader* is a command-line utility that checks for updates to Maven
dependencies and creates new Git branches for each. It is written in Python
(3.6+).

## Usage

```shell script
cd my-maven-project-repo/
git switch master  # make sure you are on your main 'master' or 'develop' branch
python3 -m mavengitupgrader
```

For more options, run `python3 -m mavengitupgrader -h`.