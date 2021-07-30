# ToeholdTools
![Python](https://img.shields.io/pypi/pyversions/thtools?style=flat-square)
[![Build](https://img.shields.io/github/workflow/status/lkn849/thtools/Build?style=flat-square)](https://github.com/lkn849/thtools/actions/workflows/autowheel.yml)
[![Documentation Status](https://img.shields.io/readthedocs/thtools?style=flat-square)](https://thtools.readthedocs.io/)
[![License](https://img.shields.io/pypi/l/thtools.svg?style=flat-square)](LICENSE)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/lkn849/thtools.svg?logo=lgtm&style=flat-square)](https://lgtm.com/projects/g/lkn849/thtools/context:python)
[![Language grade: JavaScript](https://img.shields.io/lgtm/grade/javascript/g/lkn849/thtools.svg?logo=lgtm&style=flat-square)](https://lgtm.com/projects/g/lkn849/thtools/context:javascript)

A library for the analysis of toehold switch riboregulators created by the iGEM team City of London UK 2021.

## Contents
- [ToeholdTools](#toeholdtools)
  - [Contents](#contents)
  - [What is ToeholdTools?](#what-is-toeholdtools)
  - [Installation](#installation)
  - [Run demo](#run-demo)
  - [Documentation](#documentation)
  - [License](#license)
  
## What is ToeholdTools?
ToeholdTools is a package designed to facilitate analyzing and designing toehold switches.
It's still in the making, so please leave a feature request
if there is anything else you would like to see!
## Installation
We distribute CPython wheels for Python 3.6-3.9 in all major operating systems.
We cannot build for PyPy since it not supported by all dependencies.

>Before installation, make sure you have downloaded the NUPACK library by following the instructions
[here](https://piercelab-caltech.github.io/nupack-docs/start/#installation-requirements).

You can install ToeholdTools from PyPI via pip:
```bash
python3 -m pip install thtools -U
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
[MIT](LICENSE)
