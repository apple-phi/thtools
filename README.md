# ToeholdTools

<p align="center">
  <img width="200wv" src="https://raw.githubusercontent.com/lkn849/thtools/master/src/thtools/app/web/favicon.svg" />
</p>

| Category | Status                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Repo     | [![GitHub](https://img.shields.io/github/license/lkn849/thtools?style=for-the-badge)](https://github.com/lkn849/thtools/blob/master/LICENSE) [![Documentation Status](https://img.shields.io/readthedocs/thtools?style=for-the-badge&logo=readthedocs&logoColor=white)](https://thtools.readthedocs.io/)                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Package  | ![Python](https://img.shields.io/pypi/pyversions/thtools?style=for-the-badge&logo=python&logoColor=white) [![PyPI](https://img.shields.io/pypi/v/thtools?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/thtools/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/thtools?style=for-the-badge&logo=pypi&logoColor=white)](https://pypistats.org/packages/thtools)                                                                                                                                                                                                                                                                                                                                                                                     |
| Build    | [![Build](https://img.shields.io/github/workflow/status/lkn849/thtools/Build?style=for-the-badge&logo=github)](https://github.com/lkn849/thtools/actions/workflows/autowheel.yml) [![GitHub Workflow Status (event)](https://img.shields.io/github/workflow/status/lkn849/thtools/App?label=app&style=for-the-badge&logo=github)](https://github.com/lkn849/thtools/actions/workflows/autoapp.yml) [![GitHub Workflow Status (event)](https://img.shields.io/github/workflow/status/lkn849/thtools/Test?label=tests&style=for-the-badge&logo=github)](https://github.com/lkn849/thtools/actions/workflows/autotest.yml)[![Codecov](https://img.shields.io/codecov/c/github/lkn849/thtools?style=for-the-badge&logo=codecov&logoColor=white)](https://codecov.io/gh/lkn849/thtools/) |
| Quality  | [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/lkn849/thtools.svg?logo=lgtm&style=for-the-badge)](https://lgtm.com/projects/g/lkn849/thtools/context:python) [![Language grade: JavaScript](https://img.shields.io/lgtm/grade/javascript/g/lkn849/thtools.svg?logo=lgtm&style=for-the-badge)](https://lgtm.com/projects/g/lkn849/thtools/context:javascript) [![LGTM Alerts](https://img.shields.io/lgtm/alerts/github/lkn849/thtools?label=lgtm%20alerts&style=for-the-badge&logo=lgtm)](https://lgtm.com/projects/g/lkn849/thtools/)                                                                                                                                                                                                                       |

A library for the analysis of toehold switch riboregulators created by the iGEM team City of London UK 2021.
## What is ToeholdTools?
ToeholdTools is a Python package designed to facilitate analyzing and designing toehold switches.
It's still in the making, so please leave a feature request
if there is anything else you would like to see!

It currently provides the ability to:
- Find the activation level of a toehold switch.
- Test a switch for how specific it is to the target RNA.
- Compare switch attributes across temperature ranges.
## Installation
We distribute CPython wheels for Python 3.6-3.9 in all major operating systems.
We cannot build for PyPy since it not supported by all dependencies.

>Before installation, make sure you have downloaded the NUPACK library by following the instructions
[here](https://piercelab-caltech.github.io/nupack-docs/start/#installation-requirements).
>If you are a Windows user, you will be installing both NUPACK and ToeholdTools via the Linux subsystem.

You can install a stable, pre-built version of ToeholdTools from PyPI via pip:
```bash
python3 -m pip install -U thtools
```

Alternatively, you can build the latest development version of the project from source yourself:
```bash
python3 -m pip install -U https://github.com/lkn849/thtools.git
```
If you have [npm](https://nodejs.org/en/download/) installed, this will also build the demo app.

## Run demo
There is a demo app that displays the core functionality of the module:
```bash
python3 -m thtools
```

## Documentation
The full API reference and developer notes can be found [here](https://thtools.readthedocs.io).

## License
[MIT.](https://github.com/lkn849/thtools/blob/master/LICENSE) © Copyright 2021, Lucas Ng.