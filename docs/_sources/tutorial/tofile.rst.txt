Writing Data To File
====================

A :py:class:`fld_data.FldData` instance can be written to a new field file by the
:py:meth:`fld_data.FldData.tofile` method.  This produces a valid field file that can be used
for restarting a Nek simulation and plotting in ParaView or VisIt.

In this demo, we:

    1. Read a field file
    2. Convert the temperature field from Kelvin to Celsius
    3. Re-write the data to a new field file

First, we read the file:

.. code-block:: pycon

    >>> from fld_data import FldData
    >>> f = FldData.fromfile('demos/data/test0.f00001')

Then, we convert to Celsius

.. code-block:: pycon

    >>> f.t += 273.15

Finally, we write to new file:

.. code-block:: pycon

    >>> f.tofile('celsius0.f00001')

.. warning::

    :py:meth:`fld_data.FldData.tofile` can use an arbitrary filename, but downstream applications
    (such a Nek restarts, ParaView, and VisIt) expect specifically-formatted filenames.  See the
    Nek documentation for a description of the filename format.
