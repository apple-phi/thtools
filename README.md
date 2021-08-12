# ToeholdTools
![Python](https://img.shields.io/pypi/pyversions/thtools?style=flat-square)
[![GitHub](https://img.shields.io/github/license/lkn849/thtools?style=flat-square)](https://github.com/lkn849/thtools/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/thtools?style=flat-square)](https://pypi.org/project/thtools/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/thtools?style=flat-square)](https://pypistats.org/packages/thtools)
[![Build](https://img.shields.io/github/workflow/status/lkn849/thtools/Build?style=flat-square)](https://github.com/lkn849/thtools/actions/workflows/autowheel.yml)
[![Documentation Status](https://img.shields.io/readthedocs/thtools?style=flat-square)](https://thtools.readthedocs.io/)
[![Codecov](https://img.shields.io/codecov/c/github/lkn849/thtools?style=flat-square)](https://codecov.io/gh/lkn849/thtools/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/lkn849/thtools.svg?logo=lgtm&style=flat-square)](https://lgtm.com/projects/g/lkn849/thtools/context:python)
[![Language grade: JavaScript](https://img.shields.io/lgtm/grade/javascript/g/lkn849/thtools.svg?logo=lgtm&style=flat-square)](https://lgtm.com/projects/g/lkn849/thtools/context:javascript)
[![LGTM Alerts](https://img.shields.io/lgtm/alerts/github/lkn849/thtools?style=flat-square)](https://lgtm.com/projects/g/lkn849/thtools/)

A library for the analysis of toehold switch riboregulators created by the iGEM team City of London UK 2021.
## What is ToeholdTools?
ToeholdTools is a package designed to facilitate analyzing and designing toehold switches.
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

You can install ToeholdTools from PyPI via pip:
```bash
python3 -m pip install -U thtools
```

Alternatively, you can build the latest development version of the project from source yourself:
```bash
python3 -m pip install git+https://github.com/lkn849/thtools.git
```

## Run demo
There is a demo app that displays the core functionality of the module:
```bash
python3 -m thtools
```

## Documentation
The full API reference and developer notes can be found [here](https://thtools.readthedocs.io).

## License
[MIT](https://github.com/lkn849/thtools/blob/master/LICENSE)