import numpy as np
import re
from fld_header import FldHeader
from fld_data_base import FldDataBase
import typing


class FldData(FldDataBase):
    """ Contains the header and field data of a binary Nek5000 field file.

    The constructor is typically not used directly.  Most users will prefer to use :py:meth:`FldData.fromfile` or
    :py:meth:`FldData.fromvalues`.

    The parameters representing fields (``coords``, ``u``, ``p``, ``t``, and ``s``) must have sizes that are consistent with
    ``header``.  For example, the scalar field ``p`` must have size equal to
    ``(header.nelt * header.nx1 * header.ny1 * header.nz1,)``.  The constructor will raise a ``ValueError`` if the sizes are
    inconsistent.

    Parameters
    ----------
    header
        An instantiated :py:class:`fld_header.FldHeader` object.
    coords
        Array of global element coordinates.
        Must have shape = ``(header.nelt, header.nx1 * header.ny1 * header.nz1, header.ndims)``.  Default is ``None``.
    u
        Array of velocities.  Must have shape = ``(header.nelt, header.nx1 * header.ny1 * header.nz1, header.ndims)``. Default is ``None``.
    p
        Array of pressures.  Must have shape = ``(header.nelt * header.nx1 * header.ny1 * header.nz1,)``. Default is ``None``.
    t
        Array of temperatures.  Must have shape = ``(header.nelt * header.nx1 * header.ny1 * header.nz1,)``. Default is ``None``.
    s
        Array of passive scalars.  Must have shape = ``(header.nscalars, header.nelt * header.nx1 * header.ny1 * header.nz1)``. Default is ``None``.

    Raises
    ------
    ValueError
        If the size of any field is inconsistent with the header.

    """

    def __init__(self,
                 header: FldHeader,
                 coords: np.ndarray = None,
                 u: np.ndarray = None,
                 p: np.ndarray = None,
                 t: np.ndarray = None,
                 s: np.ndarray = None):

        super().__init__(header)

        self._coords = np.array([], self.float_type)
        self._u = np.array([], self.float_type)
        self._p = np.array([], self.float_type)
        self._t = np.array([], self.float_type)
        self._s = np.array([], self.float_type)

        if coords is not None:
            self.coords = coords
        if u is not None:
            self.u = u
        if p is not None:
            self.p = p
        if t is not None:
            self.t = t
        if s is not None:
            self.s = s

    @classmethod
    def fromfile(cls, filename: str):

        # Convenience functions
        def notify(msg: str):
            print("[{}] : {}".format(filename, msg))

        def error(msg: str):
            raise Exception("[{}] : {}".format(filename, msg))

        h = FldHeader.fromfile(filename)

        coords = np.array([])
        u = np.array([])
        p = np.array([])
        t = np.array([])
        s = np.array([])
        nxyz = h.nx1 * h.ny1 * h.nz1

        notify("Attempting to fields from rdcode {}".format(h.rdcode))

        with open(filename, 'rb') as f:

            # Begin parsing fields after the _header
            f.seek(136 + h.nelt * h.int_type.itemsize)

            # Parse rdcode into list (e.g., "XUS01" is parsed into ['X', 'U', 'S01']
            code_list = [s.upper() for s in re.split(r'(\D\d*)', h.rdcode) if s]
            for code in code_list:

                # Coordinate data
                if code == 'X':
                    notify("Located coordinates X")
                    size = h.ndims * h.nelt * nxyz * h.float_type.itemsize
                    coords = np.frombuffer(f.read(size), dtype=h.float_type).reshape(h.nelt, h.ndims, nxyz)

                # Velocity field
                elif code == 'U':
                    notify("Located velocity field U")
                    size = h.ndims * h.nelt * h.nx1 * h.ny1 * h.nz1 * h.float_type.itemsize
                    u = np.frombuffer(f.read(size), dtype=h.float_type).reshape(h.nelt, h.ndims, nxyz)

                # Pressure field
                elif code == 'P':
                    notify("Located pressure field P")
                    size = h.nelt * h.nx1 * h.ny1 * h.nz1 * h.float_type.itemsize
                    p = np.frombuffer(f.read(size), dtype=h.float_type).reshape(h.nelt, nxyz)

                # Temperature field
                elif code == 'T':
                    notify("Located temperature field T")
                    size = h.nelt * h.nx1 * h.ny1 * h.nz1 * h.float_type.itemsize
                    t = np.frombuffer(f.read(size), dtype=h.float_type).reshape(h.nelt, nxyz)

                # Passive scalars
                elif code.startswith('S'):
                    try:
                        nscalars = int(code[1:])
                    except ValueError:
                        error("Couldn'_t parse number of passive scalar fields")
                    else:
                        notify("Located {} passive scalar fields".format(nscalars))
                        size = nscalars * h.nelt * h.nx1 * h.ny1 * h.nz1 * h.float_type.itemsize
                        s = np.frombuffer(f.read(size), dtype=h.float_type).reshape(nscalars, h.nelt, nxyz)

                else:
                    error("Warning: Unsupported rdcode '{}'".format(code))

        return cls(header=h, coords=coords, u=u, p=p, t=t, s=s)

    @classmethod
    def fromvalues(cls,
                   nelgt: int,
                   nx1: int,
                   ny1: int,
                   nz1: int,
                   nelt: int,
                   time: float = 0.0,
                   iostep: int = 0,
                   fid0: int = 0,
                   nfileoo: int = 1,
                   p0th: float = 0.0,
                   if_press_mesh: bool = False,
                   float_type: np.dtype = np.dtype(np.float32),
                   int_type: np.dtype = np.dtype(np.int32),
                   glel: np.ndarray = None,
                   coords: np.ndarray = None,
                   u: np.ndarray = None,
                   p: np.ndarray = None,
                   t: np.ndarray = None,
                   s: np.ndarray = None):
        """ Creates a :py:class:`FldData` object from the given data values.

        Parameters
        ----------
        nelgt
            Number of global elements
        nx1
            Number of GLL gridpoints along x-axis
        ny1
            Number of GLL gridpoints along y-axis
        nz1
            Number of GLL gridpoints along z-axis
        nelt
            Number of elements in this file
        time
            Absolute simulation time of this file's state
        iostep
            I/O timestep of this file's state
        fid0
            Index of this file, with respect to all files produced at this I/O step
        nfileoo
            Number of files produced at this I/O step
        p0th
            __
        if_press_mesh
            States whether pressure mesh is being used
        float_type
            Data type used for floating point numbers in this file
        int_type
            Data type used for integers in this file
        glel
            Array of global element indices; shape must be ``(nelt,)``
        coords
            Array of element coordinates; shape must be ``(nelt, ndims, nx1 * ny1 * nz1)``
        u
            Array representing velocity field; shape must be ``(nelt, ndims, nx1 * ny1 * nz1)``
        p
            Array representing pressure field; shape must be ``(nelt, nx1 * ny1 * nz1,)``
        t
            Array representing temperature field; shape must be ``(nelt, nx1 * ny1 * nz1,)``
        s
            Array representing all passive scalar field; shape must be ``(nscalars, nelt, nx1 * ny1 * nz1)``

        Returns
        -------
        FldData
            A new instance of :py:class:`FldData`

        """

        header = FldHeader(nelgt=nelgt, nx1=nx1, ny1=ny1, nz1=nz1, nelt=nelt, time=time, iostep=iostep, fid0=fid0,
                           nfileoo=nfileoo, p0th=p0th, if_press_mesh=if_press_mesh, float_type=float_type,
                           int_type=int_type, glel=glel)

        return cls(header=header, coords=coords, u=u, p=p, t=t, s=s)

    def tofile(self, filename: str):
        """ Writes the data of this object to a binary Nek5000 field file.

        If ``filename`` already exists, it is silently overwritten.

        Parameters
        ----------
        filename
            The name of the desired field file

        """
        self._header.tofile(filename)
        with open(filename, 'ab') as f:
            f.write(self._coords.tobytes())
            f.write(self._u.tobytes())
            f.write(self._p.tobytes())
            f.write(self._t.tobytes())
            f.write(self._s.tobytes())
            self._write_metadata(f)

    def _write_metadata(self, file: typing.BinaryIO):
        """
        Writes metadata necessary for an open file object.  Uses current file offset.

        :param file: An open file object.  Must be in binary mode.
        """

        def vec_field_metadata(v):
            # For coords and u
            cols = []
            for i in range(self.ndims):
                cols.append(np.min(v[:, i, :], axis=1))
                cols.append(np.max(v[:, i, :], axis=1))
            return np.column_stack(cols)

        def scal_field_metadata(v):
            # For p, t, and each field in s
            return np.column_stack([np.min(v, axis=-1), np.max(v, axis=-1)])

        file.write(vec_field_metadata(self._coords).tobytes())
        file.write(vec_field_metadata(self._u).tobytes())
        file.write(scal_field_metadata(self._p).tobytes())
        file.write(scal_field_metadata(self._t).tobytes())
        for i in range(self._s.shape[0]):
            file.write(scal_field_metadata(self._s[i, :, :]).tobytes())

    @FldDataBase.coords.setter
    def coords(self, other: np.ndarray):
        if other.size != 0 and other.shape != (self.nelt, self.ndims, self.nx1 * self.ny1 * self.nz1):
            raise ValueError("Incorrect shape for coords: coords.shape must equal (nelt, ndims,  nx1 * ny1 * nz1)")
        self._coords = other.astype(self.float_type)
        self._set_rdcode()

    @FldDataBase.u.setter
    def u(self, other: np.ndarray):
        if other.size != 0 and other.shape != (self.nelt, self.ndims, self.nx1 * self.ny1 * self.nz1):
            raise ValueError("Incorrect shape for u: u.shape must equal (nelt, ndims, nx1 * ny1 * nz1)")
        self._u = other.astype(self.float_type)
        self._set_rdcode()

    @FldDataBase.p.setter
    def p(self, other: np.ndarray):
        if other.size != 0 and other.shape != (self.nelt, self.nx1 * self.ny1 * self.nz1,):
            raise ValueError("Incorrect shape for p: p.shape must equal (nelt * nx1 * ny1 * nz1,)")
        self._p = other.astype(self.float_type)
        self._set_rdcode()

    @FldDataBase.t.setter
    def t(self, other: np.ndarray):
        if other.size != 0 and other.shape != (self.nelt, self.nx1 * self.ny1 * self.nz1,):
            raise ValueError("Incorrect shape for t: t.shape must equal ``(nelt * nx1 * ny1 * nz1,)``")
        self._t = other.astype(self.float_type)
        self._set_rdcode()

    @FldDataBase.s.setter
    def s(self, other: np.ndarray):
        if other.size != 0 and (
                len(other.shape) != 3 or other.shape[1:] != (self.nelt, self.nx1 * self.ny1 * self.nz1)):
            raise ValueError(
                "Incorrect shape for s: s.shape must equal (x, nelt, nx1 * ny1 * nz1) for arbitrary number of scalars x")
        self._s = other.astype(self.float_type)
        self._set_rdcode()
