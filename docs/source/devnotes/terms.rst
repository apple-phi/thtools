Terminology
===========

This is a collection of definitions for terms which appear frequently in the documentation and codebase.

.. list-table::
    :widths: auto
    :align: center
    :header-rows: 0

    * - **activation**
      - The state of a toehold switch being correctly unbound for translation, or the probability of.
        This equivalent to the proportion of toehold switch molecules which have all of:

        * an unbound RBS
        * an unbound AUG
        * an unbound post-AUG region
    * - **unbinding**
      - The state of an RNA subsequence being unpaired in a way
        that would hinder toehold switch activation,
        or the probability of.
    * - **RBS unbinding**
      - The probability of every base in the RBS subsequence being unpaired.
    * - **AUG unbinding**
      - The probability of every base in the first AUG sequence following the RBS being unpaired.
    * - **post-AUG unbinding**
      - The probability of every base in the sequence following the start codon
        *not being bound to any base in the start codon or any base upstream of the start codon.*