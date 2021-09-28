Welcome to ToeholdTools!
========================

.. toctree::
   :hidden:
   :caption: Basic usage
   :glob:

   basic/*

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
ToeholdTools is a package designed to facilitate analyzing and designing toehold switch riboregulators.
It's still in the making, so please leave a feature request
if there is anything else you would like to see!

It currently provides the ability to:

* Find the activation level of a toehold switch.
* Test a switch for how specific it is to the target RNA.
* Compare switch attributes across temperature ranges.

Check out the sidebar on the left to see the basics of how to use ToeholdTools.

How it works
------------
At the core of ToeholdTools is the idea of testing how specific your toehold switch is to the target RNA.
This is essential if you aim to use the switch in any kind of diagnostic test!
To do so, we simulate how the switch will behave when in solution with each RNA from a large database of RNAs.

Each RNA will form a set of complexes with the toehold switch, each complex having with its own concentration.
Using Boltzmann sampling, we calculate the probability of each complex being unfolded in a way that permits translation
(":ref:`activating<Terminology>`" the toehold switch) and hence we weight each complex's overall probability with its concentration to generate
an overall activation level with the RNA.

This results in a table of the activation level of the toehold switch with each RNA strand, and hence we can
calculate the specificity of the toehold switch across the entire the RNA dataset by the following expression.
Let :math:`a` be the target RNA (we assume that the highest activating RNA is the target in most cases) and
:math:`b` be the RNA with the highest activation level in the set of all RNAs in the database which are not :math:`a`
(i.e., the RNA with the second highest activation level).
Defining :math:`S` as the specificity percentage:

.. math::
   S = \frac{\mathbb {P} (a) - \mathbb {P} (b)}{\mathbb {P} (a)} \times 100\%