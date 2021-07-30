Tracking Progress
=================

.. currentmodule:: thtools

Since testing against databases which are thousands of RNAs long will take several minutes,
we provide a few options you have if you wish to view the progress.

Firstly, you can set :attr:`thtools.core.USE_TIMER` to True.
This will make the test print from each CPU core,
both when it has finished running the NUPACK simulation
and also when it has finished processing the result.
This will not slow down the test at all,
but may not be helpful since the majority of the time is taken up by NUPACK's algorithms,
so there will not be much time difference
between the first set of printing (after the initial simulations) and the end of the whole test itself.

Second, you can use the :meth:`generate` methods of :class:`~thtools.core.ToeholdTest`
and :class:`~thtools.crt.CelsiusRangeTest` in lieu of :meth:`run`.
This will return a generator that you can iterate through
using something like `tqdm <https://github.com/tqdm/tqdm>`_ to track the progress.
By itself, that will not be helpful, since there is only one worker process per CPU core
by default (and so the progress bar will not update until the very end),
but you can change that using the :attr:`chunks_per_node` argument.

.. note::
    For :class:`~thtools.core.ToeholdTest` only, the caveat is that using many small chunks
    instead of few large ones reduces performance significantly since NUPACK cannot cache
    free energy values across separate simulations.

For example:

.. code-block:: python

    import thtools as tt
    from tqdm.autonotebook import tqdm

    my_fasta = tt.FParser.fromspecies("Acyrthosiphon pisum")  # grab miRNAs from miRBase
    my_test = tt.autoconfig(
        ths=(
            "UUAGCCGCUGUCACACGCAC"
            "AGGGAUUUACAAAAAGAGGA"
            "GAGUAAAAUGCUGUGCGUGC"
            "ACCAUAAAACGAACAUAGAC"
        ),
        rbs="AGAGGAGA",
        triggers=my_fasta.seqs,
        names=my_fasta.ids,  # maps each name -> trigger
        const_rna=[],
        set_size=1,
    )
    my_generator = my_test.generate(max_size=3, n_samples=100, chunks_per_node=10)
    for _ in tqdm(my_generator, total=my_fasta.num):
        pass  # iterate through progress bar
    result = my_test.result
    print(result.prettify(dp=4))


Naturally, since the :meth:`generate` methods return generators, not the results,
you cannot receive the result the same way as in :meth:`run`.
However, the results of both :class:`~thtools.core.ToeholdTest`
and :class:`~thtools.crt.CelsiusRangeTest` are stored in the :attr:`result` attribute.