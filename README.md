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

## Install

```shell script
pip3 install mavengitupgrader
```

## Publishing

This project is distributed to [PyPI.org] in order to be freely available and
easily downloadable from there.

### Automated

This GitHub repository has been configured with a [GitHub Action] that will
automatically trigger the
[`pythonpublish.yml`](.github/workflows/pythonpublish.yml) workflow to publish
this project to PyPi every time a release is created in this GitHub repository.

### Manual

If you must publish this project manually to PyPi, do this:

```shell script
pip3 install twine
python3 setup.py sdist
twine --repository mavengitupgrader  # optional, use if PyPI token in ~/.pypirc
twine upload dist/*
```



<!-- Links -->
[PyPI.org]: https://pypi.org/project/mavengitupgrader/
[GitHub Action]: https://pypi.org/project/mavengitupgrader/
