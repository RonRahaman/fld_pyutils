Data Representation
===================

Header Data
-----------

The header of a field file includes metadata about:
    * The number of elements (``nelt``) in the given file
    * The number of GLL gridpoints (``nx1``, ``ny1``, and ``nz1``)
    * The number of physical dimensions in the simulation (``ndims``) [#f1]_
    * The number of passive scalar fields (``nscalars``)
    * The size of integer types (``int_type``).  In Fld Utils, this is represented
      as a :py:class:`numpy.dtype`
    * The size and endianness of floating-point types (``float_type``).  In Fld Utils, this is represented
      as a :py:class:`numpy.dtype`, which contains information about size and endianness.
    * Other items, which are documented in :py:class:`fld_header.FldHeader`

Index, Coordinate, and Field Data
---------------------------------

The main contents of the file include arrays of global element indices, element coordinates,
and the fields themselves.  In Fld Utils, these are all represented as :py:class:`numpy.ndarray`.
The data types of these arrays must be consistent with ``int_type`` or  ``float_type``, as described
by the header. The shapes of these arrays must be consistent with the sizes described by the header:
    * The global element IDs (``glel``) must have shape ``(nelt,)``
    * The element coordinates (``coords``) must have shape ``(ndims, nelt * nx1 * ny1 * nz1)``
    * The velocity field (``u``) must have shape ``(ndims, nelt * nx1 * ny1 * nz1)``
    * The pressure field (``p``) must have shape ``(nelt * nx1 * ny1 * nz1,)``
    * The temperature field (``t``) must have shape ``(nelt * nx1 * ny1 * nz1,)``
    * The passive scalar fields (``s``) must have shape ``(nscalars, nelt * nx1 * ny1 * nz1)``.

Ensuring Data Consistency
-------------------------

Data consistency is internally managed by the objects in Fld Utils.  Much of it (such as handling byte data)
needn't ever be managed directly by the user.  Furthermore, when the user attempts an inconsistent operation
(such as attempting to set an incorrectly-sized field), the user is issued an error.  It is intended that the
user can never -- either knowlingly or unknowlingly -- create an inconsistent field file.

The following information describes internal data management and **is not necessary knowledge for the user.**

When reading from file, the index, coordinate, and field data are parsed using
:py:class:`numpy.frombuffer`.  This method takes a byte object, whose size is determined by the header data.
This method also takes a parameter for :py:class:`numpy.dtype`, which is inferred
from ``int_type`` and ``float_type`` in the header of the field file; once the datatype is specified, the
bytewise representation of the data can be internally managed by NumPy.

When updating field the field data, the user must provide a :py:class:`numpy.ndarray` of the correct shape.
Setting this data is handled by a managed attribute, which raises an error if the shape is incorrect.
Conversion to the correct datatype is also handled automatically.

When writing data, a byte object is constructed from :py:meth:`numpy.ndarray.tobytes`.   The bytewise
representation is handled automatically.

.. rubric:: Footnotes

.. [#f1] The number of dimensions is inferred from the value of ``nz1``.  If ``nz1 == 1``,
    then the simulation is assumed to be 2D.  Otherwise, the simulation is 3D.
