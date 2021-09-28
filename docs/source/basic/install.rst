Installation
============

There are two different ways you can use this software tool. It is designed to be called from Python scripts,
but users who are not comfortable with programming in Python and/or do not need full control over simulation
parameters can download the package wrapped as a desktop app with an easy-to-use graphical user interface.

Python package
--------------

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
This displays the core functionality of the module and can be accessed by running:

.. code-block:: bash

   $ python3 -m thtools


Standalone desktop app
----------------------

To download the app by itself, choose the file in `this folder <https://mega.nz/folder/SzRz0QhC#80ihtLxaMKfz0JKARmqryw>`_
which matches your operating system. We recommend that you have Google Chrome installed and have not tested the app
where Chrome is unavailable.

.. important::
    As with the Python package itself, Windows environments are not natively supported.
    You will need a virtual machine to use this app if you are a Windows user.

This app is identical to the demo mentioned above, except that it embeds an installation of the Python interpreter
so that no programming experience is necessary.

If you open the app you and get a message saying that it cannot be verified for lack of malware,
`right click` and click `open` to force your operating system to launch it.