Welcome to ToeholdTools!
========================

.. toctree::
   :hidden:
   :caption: API reference
   
   api/core.rst
   api/crt.rst
   api/fasta.rst
   api/utils.rst

.. toctree::
   :hidden:
   :caption: Developer notes
   :glob:

   devnotes/*

.. automodule:: thtools
   :no-members:

What is this?
-------------
ToeholdTools is a package designed to facilitate analyzing and designing toehold switches.
It's still in the making, so please leave a feature request
if there is anything else you would like to see!

It currently provides the ability to:

* Find the activation level of a toehold switch.
* Test a switch for how specific it is to the target RNA.
* Compare switch attributes across temperature ranges.

Installation
------------
We distribute CPython wheels for Python 3.6-3.9 in all major operating systems.
We cannot build for PyPy since it not supported by all dependencies.

.. important::
   Before installation, make sure you have downloaded the NUPACK library by following the instructions
   `here <https://piercelab-caltech.github.io/nupack-docs/start/#installation-requirements>`_.
   If you are a Windows user, you will be installing both NUPACK and ToeholdTools via the Linux subsystem.

You can install a stable, pre-built version of ToeholdTools from PyPI via pip:

.. code-block:: bash

   $ python3 -m pip install -U thtools

Alternatively, you can build the latest development version of the project from source yourself:

.. code-block:: bash

   $ python3 -m pip install -U https://github.com/lkn849/thtools.git

If you have `npm <https://nodejs.org/en/download/>`_ installed, this will also build the demo app.

Run demo
--------
There is a demo app that displays the core functionality of the module:

.. code-block:: bash

   $ python3 -m thtools

Quick start
-----------
This is a walkthrough of finding a toehold switch's specificity.
If you don't need full customizability, the :func:`~thtools.utils.autoconfig` function can simplify the simulation parameters.

First import ToeholdTools:

.. code-block:: python

   import thtools as tt

Now define the toehold switch and ribosome binding site used.
The example used is team City of London UK (2021)'s switch for hsa-miR-210-3p:

.. code-block:: python

   ths = "UUAGCCGCUGUCACACGCACAGGGAUUUACAAAAAGAGGAGAGUAAAAUGCUGUGCGUGCACCAUAAAACGAACAUAGAC"
   rbs = "AGAGGAGA"

Then load the RNA sequences you want test against your toehold switch.
We'll use the a subsection of the *Homo sapiens* mature `miRNA database <https://www.mirbase.org>`_,
which ships pre-packaged with ToeholdTools and sorted by species:

.. code-block:: python

   my_fasta = tt.FParser.fromspecies("Homo sapiens")[295:305] # slice a small chunk of the database
   my_rna_triggers = my_fasta.seqs
   my_rna_names = my_fasta.ids # optional argument

.. We don't have any RNAs we want to keep constant:
.. .. code-block:: python
..    const_rna = [] # optional

.. And since we want to only test one potentially triggering RNA with the toehold switch at a time,
.. set the combinatoric set size to 1:
.. .. code-block:: python
..    set_size = 1 # this is the default


Now setup the :class:`~thtools.core.ToeholdTest` simulation and run it:

.. code-block:: python

   my_test = tt.autoconfig(ths, rbs, my_rna_triggers, names=my_rna_names)
   my_result = my_test.run(
      max_size=3, # the largest size of RNA complex to consider
      n_samples=100, # the number of Boltzmann samples to take of each complex's secondary structure
   )
   print(my_result.prettify(
   dp=5 # number of decimal places to show (optional argument)
   ))

And here is the output:

.. code-block::

   THS: UUAGCCGCUGUCACACGCACAGGGAUUUACAAAAAGAGGAGAGUAAAAUGCUGUGCGUGCACCAUAAAACGAACAUAGAC
   THS concentration: 1e-07
   RBS: AGAGGAGA
   # tests: 10
   Constant RNAs: []
   Concentrations of constant RNAs: []
   Temperature /°C: 37.0
   Max. complex size: 3
   Sample number: 100
   Target RNA: CUGUGCGUGUGACAGCGGCUGA
   Specificity %: 99.99929501947653
   Specificity SE: 0.03086125411972951

   +-----------------+-------------------------+--------------+-----------------+-----------------+----------------------+----------------+
   | Name            | Sequence                | Activation % | RBS unbinding % | AUG unbinding % | Post-AUG unbinding % | Standard Error |
   +-----------------+-------------------------+--------------+-----------------+-----------------+----------------------+----------------+
   | hsa-miR-210-3p  | CUGUGCGUGUGACAGCGGCUGA  | 73.99997     | 89.00000        | 76.99996        | 77.99996             | 4.38634        |
   | hsa-miR-211-5p  | UUCCCUUUGUCAUCCUUCGCCU  | 0.00052      | 89.71612        | 1.20635         | 0.00256              | 0.02273        |
   | hsa-miR-210-5p  | AGCCCCUGCCCACCGCACACUG  | 0.00000      | 89.71684        | 1.20570         | 0.00006              | 0.00120        |
   | hsa-miR-212-5p  | ACCUUGGCUCUAGACUGCUUACU | 0.00000      | 89.72340        | 2.79487         | 0.00005              | 0.00120        |
   | hsa-miR-214-5p  | UGCCUGUCUACACUUGCUGUGC  | 0.00000      | 89.66515        | 2.58864         | 0.00003              | 0.00120        |
   | hsa-miR-212-3p  | UAACAGUCUCCAGUCACGGCC   | 0.00000      | 90.48688        | 2.80960         | 0.00004              | 0.00113        |
   | hsa-miR-214-3p  | ACAGCAGGCACAGACAGGCAGU  | 0.00000      | 89.22156        | 2.57101         | 0.00000              | 0.00041        |
   | hsa-miR-211-3p  | GCAGGGACAGCAAAGGGGUGC   | 0.00000      | 97.53812        | 1.63230         | 0.00001              | 0.00040        |
   | hsa-miR-208b-5p | AAGCUUUUUGCUCGAAUUAUGU  | 0.00000      | 89.71161        | 2.79455         | 0.00004              | 0.00000        |
   | hsa-miR-208b-3p | AUAAGACGAACAAAAGGUUUGU  | 0.00000      | 89.71643        | 2.79433         | 0.00004              | 0.00000        |
   +-----------------+-------------------------+--------------+-----------------+-----------------+----------------------+----------------+

.. note:: Your output might have slightly different values since Boltzmann sampling is pseudo-random.

Since hsa-miR-210-3p has by far the highest activation of all the RNAs tested (as expected),
this switch is highly specific to the desired target!

