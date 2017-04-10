.. Serial Mock documentation master file, created by
   sphinx-quickstart on Fri Apr 07 17:09:11 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Serial Mock's documentation!
=======================================

I wrote SerialMock in order to make testing interfaces with devices a bit easier. I felt like there was no good existing solution to this problem
you can install it with any one of

Requirements
------------

  - Python2.7
  - a serial port to bind to (whether it is a hardware null modem or software should not matter).

     - *in general you can use com0com for windows systems, and socat for *nix systems in order to create a software null modem*

  .. seealso::

    .. toctree::
      :maxdepth: 2

      nullmodem



Installation
------------

| :code:`setup.py install`
| or :code:`pip install .`
| or install it from pipy with :code:`pip install serial_mock`




API Reference
-------------

.. toctree::
   :maxdepth: 1

   serial_mock
   decorators


Tools
-----

.. toctree::
   :maxdepth: 2

   nullmodem
   teminalprogs
   cli_util







Examples
--------

.. toctree::
   :maxdepth: 1

   tutorial
   examples

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

