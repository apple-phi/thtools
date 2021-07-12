# ToeholdTools
[![Build](https://github.com/lkn849/thtools/actions/workflows/autowheel.yml/badge.svg)](https://github.com/lkn849/thtools/actions/workflows/autowheel.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A library for the analysis of toehold switch riboregulators made by the iGEM team City of London UK 2021. We provide tools for characterizing toehold switches for their specificity to the target RNA, with future plans to expand to design tools.

## Installation
We distribute CPython wheels for Python 3.6-3.9 in all major operating systems. Unfortunately, there is no use distributing PyPy builds since it not supported by all dependencies.

Before installation, make sure you have downloaded the NUPACK library by following the instructions [here](https://piercelab-caltech.github.io/nupack-docs/start/#installation-requirements).

You can install ToeholdTools from PyPI via pip:
```bash
python3 -m pip install thtools -U
```

Alternatively, you can build the project from source yourself:
```bash
python3 -m pip install git+https://github.com/lkn849/thtools.git
```

## Analyzing toehold switches
### How it works
We put each set of RNAs you are testing individually into a virtual test tube with the toehold switch. Then, we use the [NUPACK](https://github.com/beliveau-lab/NUPACK) amino acid analysis library to simulate the interactions. Finally, we observe the resulting toehold switch secondary structures to see the probability of your toehold switch activating when that set of RNAs is present.

For performance, the majority of the analysis sub-module is compiled via [Cython](https://github.com/cython/cython), and uses the [Pathos](https://github.com/uqfoundation/pathos) multiprocessing sub-module for distributing work across CPU cores. We are also considering GIL-free processing using OpenMP.

### Quick start
If you don't care about full customizability, using the higher level wrapper is recommended:
```python
import thtools as tt

my_test = tt.autoconfig(
    ths = [ # your toehold switch
    "UUAGCCGCUGUCACACGCAC"
    "AGGGAUUUACAAAAAGAGGA"
    "GAGUAAAAUGCUGUGCGUGC"
    "ACCAUAAAACGAACAUAGAC" # NOTE: the lack of commas here is Python syntax for writing a long string across several lines.
    ],
    rbs="AGAGGAGA", # the ribosome binding site you used
    triggers=[ # the set of individual RNAs which potentially trigger the toehold switch you are testing
        "CUGUGCGUGUGACAGCGGCUGA",
        "CUAUACAAUCUACUGUCUUUC",
        "CUGUACAGCCUCCUAGCUUUCC",
    ],
    const_rna=[], # any other strands you want to keep constant and present in every test tube
    set_size=1,
    # autoconfig will generate combinatoric trigger sets of sizes up to and including set_size.
    # Useful for testing logic gate toehold switches.
    # But if you only want to test one a a time as standard, leave as 1.
)
my_results = my_test.run(
    max_size=3,  # the maximum RNA complex size to consider
    n_samples=100,  # the number of Boltzmann samples to take of each complex's secondary structure
)
print(my_results)
```
`autoconfig` returns a `ToeholdTest` instance which can be run as shown above. You can also construct the `ToeholdTest` yourself, but the parameter requirements are quite specific and it's often easier just to use this utility function to auto-generate it for you. Concentrations of all RNA strands is assumed to be 100nM.

This results in a `ToeholdResult` instance (which is also stored as the `result` attribute of the `ToeholdTest`).

To save the data stored in the `ToeholdResult`, you can call the `.to_csv()` method, which will return a csv string you can save to file.

### Advanced analysis
Without using the `autoconfig` function, the direct creation of a `ToeholdTest` instance is:
```python
import numpy as np
import thtools as tt

ths = { # {sequence : concentration}
    "UUAGCCGCUGUCACACGCAC"
    "AGGGAUUUACAAAAAGAGGA"
    "GAGUAAAAUGCUGUGCGUGC"
    "ACCAUAAAACGAACAUAGAC" : 1e-7
}
rbs_position = slice(34, 42) # slice of the above sequence containing the RBS
trigger_sets = np.array( # each sub-array will be individually tested with the toehold switch
    [["CUGUGCGUGUGACAGCGGCUGA"], 
     ["CUAUACAAUCUACUGUCUUUC"],
     ["CUGUACAGCCUCCUAGCUUUCC"]]
)
conc_sets = np.array( # maps a concentration to each sequence in the trigger_sets
    [[1e-7],
     [1e-7],
     [1e-7]],
    dtype=np.float64
)
const_rna = {} # {sequence : concentration}

my_test = tt.ToeholdTest(ths, rbs_position, trigger_sets, conc_sets, const_rna)
my_results = my_test.run(
    max_size=3,
    n_samples=100,
)
print(my_results)
```
The `trigger_sets` and `conc_sets` array parameters allows you to specify exactly which combinations and concentrations of RNA strands is tested with the toehold switch in each test tube. Concentrations are measured in molar (M).

You can also pass the thermodynamic model to be used using the `model` argument of both constructors. Otherwise the model is 37°C with 1.0M Na<sup>+</sup> and a stacking ensemble. For more information on specifying the model parameters see the NUPACK [documentation](https://piercelab-caltech.github.io/nupack-docs/model/).

### Notes
If you are comparing the results of the tests with the online NUPACK [website](https://www.nupack.org), it is common for a disparity whereby ToeholdTools suggests an RNA activates the toehold switch but the website disagrees. This is due to a difference in thermodynamic models used, since this package uses a newer, superior version of NUPACK with different default model parameters.

However, if you must emulate the website's behavior, you can specify the model parameters:
```python
import nupack

my_model = nupack.Model(
    ensemble="some-nupack3",
    material="rna95-nupack3",
)
```
Then you can pass that model as an argument to ToeholdTools.

### See also
- The full ToeholdTools [documentation]()

## License
[MIT](LICENSE)