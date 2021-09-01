Creating From Values
====================

A new :py:class:`fld_data.FldData` instance can be created directly from NumPy arrays using
:py:meth:`fld_data.FldData.fromvalues` method.  This is demonstrated in
``examples/demo_fromvalues_tofile.py``, found in the repo and described below.

First, we set the size of the problem, including the dimensions, number of GLL points,
and number of elements:

.. code-block:: python

    ndims = 3
    nx1 = 3
    ny1 = nx1
    nz1 = nx1
    nelgt = 10
    nelt = nelgt

We can optionally specify the datatypes of integers and floats in the file.  By default,
:py:meth:`fld_data.FldData.fromvalues` uses 32-bit ints and floats.

.. code-block:: python

    float_type = np.dtype(np.float32)
    int_type = np.dtype(np.int32)

We must explicitly set global element IDs.  In many downstream use cases, this is arbitrary.

.. code-block:: python

    glel = np.arange(1, nelt + 1)

To create the gridpoints, you can use a variety of NumPy trickery.  For demonstration purposes,
we will start with simple array of shape ``(nelt, ndim)`` and use it to construct an NumPy array of
shape  ``(nelt, ndim, nx1 * ny1 * nz1)``. The latter is the expected shape for
``FldData.coords``.

We start with these points:

.. code-block:: python

    pt =[[0.0, 0.0, 0.0],
         [0.5, 0.0, 0.0],
         [1.0, 0.0, 0.0],
         [0.0, 0.5, 0.0],
         [0.5, 0.5, 0.0],
         [1.0, 0.5, 0.0],
         [0.0, 1.0, 0.0],
         [0.5, 1.0, 0.0],
         [1.0, 1.0, 0.0],
         [0.0, 0.0, 0.5],
         [0.5, 0.0, 0.5],
         [1.0, 0.0, 0.5],
         [0.0, 0.5, 0.5],
         [0.5, 0.5, 0.5],
         [1.0, 0.5, 0.5],
         [0.0, 1.0, 0.5],
         [0.5, 1.0, 0.5],
         [1.0, 1.0, 0.5],
         [0.0, 0.0, 1.0],
         [0.5, 0.0, 1.0],
         [1.0, 0.0, 1.0],
         [0.0, 0.5, 1.0],
         [0.5, 0.5, 1.0],
         [1.0, 0.5, 1.0],
         [0.0, 1.0, 1.0],
         [0.5, 1.0, 1.0],
         [1.0, 1.0, 1.0]]

And create a coordinate array of the proper shape:

.. code-block:: python

    nxyz = nx1 * ny1 * nz1
    coords = np.empty((nelt, ndims, nxyz), dtype=float_type)
    for j in range(nelt):
        for i in range(nxyz):
            coords[j][0][i] = pt[i][0]
            coords[j][1][i] = pt[i][1]
            coords[j][2][i] = pt[i][2] + j  #offset in the z-direction by the element number

Next, we create a velocity field with some dummy values.  Like coordinates,
``FldData.u`` must have shape ``(nelt, ndim, nx1 * ny1 * nz1)``:

.. code-block:: python

    u = np.empty((nelt, ndims, nxyz), dtype=float_type)
    for j in range(nelt):
        for i in range(nxyz):
            u[j][0][i] = j + 1.0
            u[j][1][i] = (j + 1.0) * 2.0
            u[j][2][i] = (j + 1.0) * 3.0

Next, we create pressure and velocity fields with dummy values.  The expected shape of
scalar fields is ``(nelt, nx1 * ny1 * nz1)``.

.. code-block:: python

    i = 1.0
    p = np.arange(i, i + nelt * nxyz, dtype=float).reshape(nelt, nxyz)

    i = i + nelt * nxyz
    t = np.arange(i, i + nelt * nxyz, dtype=float).reshape(nelt, nxyz)

Finally, we instantiate an :py:class:`fld_data.FldData` and write it to file:

.. code-block:: python

    data = FldData.fromvalues(nx1=nx1, ny1=ny1, nz1=nz1, nelgt=nelgt, nelt=nelt,
                             glel=glel, coords=coords, p=p, u=u, t=t)

    data.tofile('fdtf0.f00001')
