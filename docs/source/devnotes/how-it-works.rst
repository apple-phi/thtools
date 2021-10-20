How it works
============

At the core of ToeholdTools is the idea of testing how specific your toehold switch is to the target RNA.
This is essential if you aim to use the switch in any kind of diagnostic test!
To do so, we simulate how the switch will behave when in solution with each RNA from a large database of RNAs.

The theory
----------
Each RNA will form a set of complexes with the toehold switch, each complex having its own concentration.
Using Boltzmann sampling, we calculate the probability of each complex being unfolded in a way that permits translation
(":ref:`activating<Terminology>`" the toehold switch) and hence we weight each complex's overall probability with its concentration to generate
an overall activation level with the RNA.

This results in a table of the activation level of the toehold switch with each RNA strand, and hence we can
calculate the specificity of the toehold switch across the entire RNA dataset by the following expression.
Let :math:`a` be the target RNA (we assume that the highest activating RNA is the target in most cases) and
:math:`b` be the RNA with the highest activation level in the set of all RNAs in the database which are not :math:`a`
(i.e., the RNA with the second highest activation level).
Defining :math:`S` as the specificity percentage:

.. math::
   S = \frac{\mathbb {P} (a) - \mathbb {P} (b)}{\mathbb {P} (a)} \times 100\%

The switch activation model
---------------------------
In order to calculate the specificity of the toehold switch we needed a way to quantify its relative activation level
by its structure. After speaking with Alexander Green we learnt that the most important requirements for a toehold switch’s
activation are both the ribosome binding site and the start codon being completely unpaired,
while the linker region after the start codon should no longer be part of that hairpin archetypal of an
unactivated toehold switch (i.e., no base in the region after the start codon should be bound to any base
in or before the start codon).

Niles Pierce and Mark Fornace from the NUPACK team informed us that the most accurate way to get a representation
of a toehold switch’s secondary structure was not by the possible structure with the lower mean free energy (MFE)
&mdash;like all previous iGEM teams using toehold switches have done&mdash;but rather by sampling from the Boltzmann
distribution of secondary structures using a Boltzmann sampler. This method has the added bonus of being faster and
more configurable than the MFE method.
