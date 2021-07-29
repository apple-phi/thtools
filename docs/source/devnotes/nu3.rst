NUPACK 3
========

If you are comparing the result of the tests with the online `NUPACK website <https://www.nupack.org>`_,
it is common for a disparity whereby ToeholdTools suggests an RNA activates the toehold switch but the website disagrees.
This is due to a difference in thermodynamic models used, since this package uses NUPACK 4 which has a superior default model.

However, if you must emulate the website's behavior, we provide the :class:`nupack.Model` subclass :class:`thtools.utils.ModelNu3`.

The majority of the ToeholdTools suite has a model parameter you can use this with.