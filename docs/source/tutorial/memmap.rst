Using Memory-Mapped Data
========================

For field files that are too large to fit in memory, you can :py:class:`fld_data_memmap.FldDataMemmap`.
This has a very similar interface to the normal :py:class:`fld_data.FldData` and for many purposes,
it can be used interchangeably.

Under the hood, :py:class:`fld_data_memmap.FldDataMemmap` uses NumPy memory maps to access segments
of the binary field file, without reading the entire file in memory.  From the
`NumPy docs <https://numpy.org/doc/stable/reference/generated/numpy.memmap.html>`_:

    "Memory-mapped files are used for accessing small segments of large files on disk,
    without reading the entire file into memory. NumPy’s memmap’s are array-like objects."

There are several ways to use a :py:class:`fld_data_memmap.FldDataMemmap`, depending on the value of the
``mode`` argument in :py:meth:`fld_data_memmap.FldDataMemmap.fromfile`.  This argument is passed
directly as the ``mode`` argument of ``numpy.memmap``.  See the
NumPy `NumPy docs <https://numpy.org/doc/stable/reference/generated/numpy.memmap.html>`_ docs for
a description of all the modes.

    * **Read-only Mode** (``mode='r'``, default): is the most memory-efficient.  In read-only mode,
      the fields in :py:class:`fld_data_memmap.FldDataMemmap` are read only; attempting to change their
      values will raise a ``ValueError``.
    * **Read/write Mode** (``mode='r+'``):  Changes to the fields are reflected in the original file.
    * **Copy-on-wrte Mode** (``mode='c'``): Changes to the fields persist in memory, but are not
      updated in the original file.  For a :py:class:`fld_data_memmap.FldDataMemmap` in copy-on-write
      mode, you can create a new file that reflects the modified files.

