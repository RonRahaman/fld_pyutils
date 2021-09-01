.. _accessing-data:

Working With Data
=================

Header Metadata
---------------

Metadata from the header can be accessed via attributes of the
:py:class:`fld_data.FldData` object.  The header metadata includes number of
dimensions, number of elements, the I/O timestep,
etc. (see the documentation of :py:class:`fld_data.FldData` for a full list).
The header data are typically **read-only** attributes that are managed
internally; this is to maintain consistency of the overall data format when
other fields are changed.

.. code-block:: pycon

    >>> f.ndims
    3
    >>> f.nscalars
    2
    >>> f.float_type
    dtype('float32')
    >>> f.nscalars = 3
    AttributeError: can't set attribute

Elements IDs, Coordinates, and Fields
-------------------------------------

An :py:class:`fld_data.FldData` object contains NumPy arrays for global
element IDs, coordinates, velocity, pressure, temperatures, and (if present)
passive scalars.  The shape of each array depends on the kind of
data that it represents.  For example, the pressure array is 1D with shape =
`(nelt * nx1 * ny1 * nz1)` whereas the velocity array is 3D with shape
`(nelt, nx1 * ny1 * nz1, ndims)`.  See the documentation of
:py:class:`fld_data.FldData` for a full list)

Reading the data is straightforward.  It can be used like like any NumPy array.

.. code-block:: pycon

    >>> from fld_data import FldData
    >>> f = FldData.fromfile('demos/data/test0.f00001')
    [scratch.f00001] : Attempting to fields from rdcode XUPTS02
    [scratch.f00001] : Located coordinates X
    [scratch.f00001] : Located velocity field U
    [scratch.f00001] : Located pressure field P
    [scratch.f00001] : Located temperature field T
    [scratch.f00001] : Located 2 passive scalar fields
    >>> f.p                   # Pressure field
    array([-8.543964e-09, -7.483058e-09, -7.243701e-09, ..., -7.243678e-09,
           -7.483029e-09, -8.543934e-09], dtype=float32)
    >>> f.p.max()             # Maximum pressure value
    2.293219e-08
    >>> f.u[f.glel == 2,:,:]  # Velocity components for global element ID 2

Modifying elements in-place is also straightforward:

.. code-block:: pycon

    >>> f.u[f.glel == 2,:,:] = 0  # Set all velocity compenents for element 2

Re-assigning arrays is internally managed to maintain consistently-shaped
arrays.  Hence, when re-assinging arrays, the shape of the new array must
match the existing shape of the metadata (with the exception of deleting
fields and changing the number of passive scalars, see below).  :py:class:`fld_data
.FldData` will raise a `ValueError` if the shape of the new array does not match.

.. code-block:: pycon

    >>> import numpy as np
    >>> f.u = np.full_like(f.u, fill_value=1.0)                                 # OK
    >>> f.u = np.full((f.nelt, f.ndims, f.nx1 * f.ny1 * f.nz1), fill_value=2.0) # Also OK
    >>> f.u = np.full((f.ndims, f.nelt, f.nx1 * f.ny1 * f.nz1), fill_value=2.0) # Oops!
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/rahaman/repos/fld_pyutils/fld_data.py", line 226, in u
        raise ValueError("Incorrect shape for u: u.shape must equal (nelt, ndims, nx1 * ny1 * nz1)")
    ValueError: Incorrect shape for u: u.shape must equal (nelt, ndims, nx1 * ny1 * nz1)


To delete a field, assign it to an empty array:

    >>> f.u = np.array([])

You may freely change the number of passive scalars, so long as each scalar
field has the correct size:

.. code-block:: pycon

    >>> f.nscalars   # There are two passive scalars
    2

.. warning::

    The managed assignments are intended to prevent accidents.
    Be aware that :py:class:`fld_data .FldData` still allows some more
    explicit NumPy operations that may create inconsistencies.  For example:

    .. code-block:: pycon

        >>> f.u.resize(100)
        >>> f.u.shape
        (100,)

    Hopefully, these operations fall outside normal usage!
