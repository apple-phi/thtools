Quick start
===========

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
We'll use the a subsection of the *Homo sapiens* mature miRNA entries in `miRBase`_,
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
   print(my_result.tabulate(
   dp=5 # number of decimal places to show (optional argument)
   ))

And here is the output:

.. code-block:: python

   +-----------------+-------------------------+--------------+-----------------+-----------------+----------------------+----------------+
   | Name            | Sequence                | Activation % | RBS unbinding % | AUG unbinding % | Post-AUG unbinding % | Standard Error |
   +-----------------+-------------------------+--------------+-----------------+-----------------+----------------------+----------------+
   | hsa-miR-210-3p  | CUGUGCGUGUGACAGCGGCUGA  | 74.99997     | 90.00000        | 80.99996        | 80.99996             | 4.33013        |
   | hsa-miR-214-5p  | UGCCUGUCUACACUUGCUGUGC  | 0.00001      | 89.71653        | 4.27968         | 0.00005              | 0.00239        |
   | hsa-miR-208b-3p | AUAAGACGAACAAAAGGUUUGU  | 0.00000      | 89.71643        | 1.15424         | 0.00004              | 0.00170        |
   | hsa-miR-210-5p  | AGCCCCUGCCCACCGCACACUG  | 0.00000      | 89.71684        | 2.53726         | 0.00006              | 0.00170        |
   | hsa-miR-212-5p  | ACCUUGGCUCUAGACUGCUUACU | 0.00000      | 89.72340        | 1.74311         | 0.00006              | 0.00170        |
   | hsa-miR-211-5p  | UUCCCUUUGUCAUCCUUCGCCU  | 0.00000      | 89.71612        | 2.53687         | 0.00276              | 0.00170        |
   | hsa-miR-208b-5p | AAGCUUUUUGCUCGAAUUAUGU  | 0.00000      | 89.71161        | 1.15708         | 0.00004              | 0.00169        |
   | hsa-miR-212-3p  | UAACAGUCUCCAGUCACGGCC   | 0.00000      | 90.48685        | 1.90022         | 0.00008              | 0.00160        |
   | hsa-miR-214-3p  | ACAGCAGGCACAGACAGGCAGU  | 0.00000      | 89.27519        | 2.70569         | 0.00001              | 0.00082        |
   | hsa-miR-211-3p  | GCAGGGACAGCAAAGGGGUGC   | 0.00000      | 97.53812        | 4.02094         | 0.00001              | 0.00056        |
   +-----------------+-------------------------+--------------+-----------------+-----------------+----------------------+----------------+

Since hsa-miR-210-3p has by far the highest activation of all the RNAs tested (as expected),
this switch is highly specific to the desired target!
There are other result display option available (notably :meth:`~thtools.core.ToeholdResult.prettify`)
so be sure to check out the full API reference in the sidebar on the left.

.. note:: Your output might have slightly different values since Boltzmann sampling is pseudo-random.