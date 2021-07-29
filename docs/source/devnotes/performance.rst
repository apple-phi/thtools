Performance
===========

For performance, :mod:`thtools.core` is compiled via `Cython <https://github.com/cython/cython>`_,
and uses :mod:`pathos.multiprocessing` for distributing work across CPU cores :cite:p:`mckerns_building_2012`.

We are also considering GIL-free processing using OpenMP for future releases.
