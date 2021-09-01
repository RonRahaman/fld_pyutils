import numpy as np
from fld_header import FldHeader
from abc import ABC, abstractmethod
import typing


class FldDataBase(ABC):

    def __init__(self, header: FldHeader):
        self._header = header

    @classmethod
    @abstractmethod
    def fromfile(cls, filename: str):
        """ Creates an :py:class:`FldData` object from the contents of a given field file

        Parameters
        ----------
        filename
            Path to a binary Nek5000 field file

        Returns
        -------
        FldData
            A new instance of  :py:class:`FldData`

        """
        pass

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

        if len(self._coords):
            file.write(vec_field_metadata(self._coords).tobytes())
        if len(self._u):
            file.write(vec_field_metadata(self._u).tobytes())
        if len(self._p):
            file.write(scal_field_metadata(self._p).tobytes())
        if len(self._t):
            file.write(scal_field_metadata(self._t).tobytes())
        for i in range(self._s.shape[0]):
            file.write(scal_field_metadata(self._s[i, :, :]).tobytes())

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        attr = dict(coords=self.coords, u=self.u, p=self.p, t=self.t, s=self.s)
        result = str(self._header)
        for k, v in attr.items():
            result += '{key} =\n{value}\n'.format(key=k, value=v)
        return result

    @property
    def nx1(self) -> int:
        """ Number of GLL gridpoints along x-axis """
        return self._header.nx1

    @property
    def ny1(self) -> int:
        """ Number of GLL gridpoints along y-axis """
        return self._header.ny1

    @property
    def nz1(self) -> int:
        """ Number of gridpoints along z-axis """
        return self._header.nz1

    @property
    def nelt(self) -> int:
        """ Number of elements in this file """
        return self._header.nelt

    @property
    def nelgt(self) -> int:
        """ Number of global elements"""
        return self._header.nelgt

    @property
    def time(self) -> float:
        """ Absolute simulation time of this file's state """
        return self._header.time

    @property
    def iostep(self) -> int:
        """ I/O timestep of this file's state """
        return self._header.iostep

    @property
    def fid0(self) -> int:
        """ Index of this file, with respect to all files produced at this I/O step """
        return self._header.fid0

    @property
    def nfileoo(self) -> int:
        """ Number of files produced at this I/O step """
        return self._header.nfileoo

    @property
    def rdcode(self) -> str:
        """ String representing the fields contained in this file """
        return self._header.rdcode

    @property
    def p0th(self) -> float:
        """ __ """
        return self._header.p0th

    @property
    def if_press_mesh(self) -> bool:
        """ States whether pressure mesh is being used """
        return self._header.if_press_mesh

    @property
    def float_type(self) -> np.dtype:
        """ Data type used for floating point numbers in this file """
        return self._header.float_type

    @property
    def int_type(self) -> np.dtype:
        """ Data type used for integers in this file """
        return self._header.int_type

    @property
    def glel(self) -> np.ndarray:
        """ Array of global element indices; shape is ``(nelt,)`` """
        return self._header.glel

    @glel.setter
    def glel(self, other: np.ndarray):
        # glel is a managed attribute of FldHeader, so no need to validate it here in FldData
        self._header.glel = other

    @property
    def ndims(self) -> int:
        """ Number of physical dimensions in this simulation """
        return self._header.ndims

    @property
    def nscalars(self) -> int:
        """ Number of passive scalars """
        return self._header.nscalars

    @property
    def coords(self) -> np.ndarray:
        """ Array of element coordinates; shape is ``(nelt, ndims, nx1 * ny1 * nz1)`` """
        return self._coords

    @coords.setter
    @abstractmethod
    def coords(self, other: np.ndarray):
        pass

    @property
    def u(self) -> np.ndarray:
        """ Array representing velocity field; shape is ``(nelt, ndims, nx1 * ny1 * nz1)``"""
        return self._u

    @u.setter
    @abstractmethod
    def u(self, other: np.ndarray):
        pass

    @property
    def p(self) -> np.ndarray:
        """ Array representing pressure field; shape is ``(nelt * nx1 * ny1 * nz1,)``"""
        return self._p

    @p.setter
    @abstractmethod
    def p(self, other: np.ndarray):
        pass

    @property
    def t(self) -> np.ndarray:
        """ Array representing temperature field; shape is ``(nelt * nx1 * ny1 * nz1,)``"""
        return self._t

    @t.setter
    @abstractmethod
    def t(self, other: np.ndarray):
        pass

    @property
    def s(self) -> np.ndarray:
        """ Array representing all passive scalar field; shape is ``(nscalars, nelt * nx1 * ny1 * nz1)``"""
        return self._s

    @s.setter
    @abstractmethod
    def s(self, other: np.ndarray):
        pass

    def _set_rdcode(self):
        """ Re-generates the rdcode based on the current fields """
        rdcode = ""
        if self.coords.size != 0:
            rdcode += "X"
        if self.u.size != 0:
            rdcode += "U"
        if self.p.size != 0:
            rdcode += "P"
        if self.t.size != 0:
            rdcode += "T"
        if self.s.size != 0:
            rdcode += "S{:02}".format(self.s.shape[0])
        self._header.rdcode = rdcode
