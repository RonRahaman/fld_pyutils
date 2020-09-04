from fld_data_base import FldDataBase
from fld_header import FldHeader
import numpy as np
import re


# TODO: This uses tofile from the base class, which probably creates some intermediate byte arrays
# Might want to see if this is significant memory disadvantage...

class FldDataMemmap(FldDataBase):

    def __init__(self,
                 header: FldHeader,
                 readonly: bool = False,
                 coords: np.ndarray = None,
                 u: np.ndarray = None,
                 p: np.ndarray = None,
                 t: np.ndarray = None,
                 s: np.ndarray = None):

        super().__init__(header)

        self._readonly = readonly
        self._coords = np.array([], self.float_type)
        self._u = np.array([], self.float_type)
        self._p = np.array([], self.float_type)
        self._t = np.array([], self.float_type)
        self._s = np.array([], self.float_type)

        if coords is not None:
            self._coords = coords
        if u is not None:
            self._u = u
        if p is not None:
            self._p = p
        if t is not None:
            self._t = t
        if s is not None:
            self._s = s

        self._set_rdcode()

    @classmethod
    def fromfile(cls, filename: str, mode: str = "r+"):

        # Validate mode
        if mode not in ('r', 'r+', 'w+', 'c'):
            raise ValueError(f"User specified mode was {mode}, but mode must be 'r', 'r+', 'w+', or 'c'")

        # Read header and get offset where field data begin
        h = FldHeader.fromfile(filename)
        nxyz = h.nx1 * h.ny1 * h.nz1
        offset = 136 + h.nelt * h.int_type.itemsize

        # Some convenience functions
        def notify(msg: str):
            print("[{}] : {}".format(filename, msg))

        def error(msg: str):
            raise Exception("[{}] : {}".format(filename, msg))

        def read_memmap(shape):
            nonlocal offset
            v = np.memmap(filename, dtype=h.float_type, offset=offset, mode=mode, shape=shape)
            offset += v.nbytes
            return v

        # Now parse everything!
        coords = None
        u = None
        p = None
        t = None
        s = None
        notify("Attempting to fields from rdcode {}".format(h.rdcode))
        code_list = [s.upper() for s in re.split(r'(\D\d*)', h.rdcode) if s]
        for code in code_list:
            # Coordinate data
            if code == 'X':
                notify("Located coordinates X")
                coords = read_memmap((h.nelt, h.ndims, nxyz))
            # Velocity field
            elif code == 'U':
                notify("Located velocity field U")
                u = read_memmap((h.nelt, h.ndims, nxyz))
            # Pressure field
            elif code == 'P':
                notify("Located pressure field P")
                p = read_memmap((h.nelt, nxyz))
            # Temperature field
            elif code == 'T':
                notify("Located temperature field T")
                t = read_memmap((h.nelt, nxyz))
            # Passive scalars
            elif code.startswith('S'):
                try:
                    nscalars = int(code[1:])
                except ValueError:
                    error("Couldn'_t parse number of passive scalar fields")
                else:
                    notify("Located {} passive scalar fields".format(nscalars))
                    s = read_memmap((nscalars, h.nelt, nxyz))
            else:
                error("Warning: Unsupported rdcode '{}'".format(code))

        return cls(header=h, readonly=(mode == 'r'), coords=coords, u=u, p=p, t=t, s=s)

    @FldDataBase.coords.setter
    def coords(self, other: np.ndarray):
        if self._readonly:
            raise AttributeError("FldDataMemmap in read-only mode does not support field assignment.")
        if other.size != 0 and other.shape != (self.nelt, self.ndims, self.nx1 * self.ny1 * self.nz1):
            raise ValueError("Incorrect shape for coords: coords.shape must equal (nelt, ndims,  nx1 * ny1 * nz1)")
        self._coords = other.astype(self.float_type)
        self._set_rdcode()

    @FldDataBase.u.setter
    def u(self, other: np.ndarray):
        if self._readonly:
            raise AttributeError("FldDataMemmap in read-only mode does not support field assignment.")
        if other.size != 0 and other.shape != (self.nelt, self.ndims, self.nx1 * self.ny1 * self.nz1):
            raise ValueError("Incorrect shape for u: u.shape must equal (nelt, ndims, nx1 * ny1 * nz1)")
        self._u = other.astype(self.float_type)
        self._set_rdcode()

    @FldDataBase.p.setter
    def p(self, other: np.ndarray):
        if self._readonly:
            raise AttributeError("FldDataMemmap in read-only mode does not support field assignment.")
        if other.size != 0 and other.shape != (self.nelt, self.nx1 * self.ny1 * self.nz1,):
            raise ValueError("Incorrect shape for p: p.shape must equal (nelt * nx1 * ny1 * nz1,)")
        self._p = other.astype(self.float_type)
        self._set_rdcode()

    @FldDataBase.t.setter
    def t(self, other: np.ndarray):
        if self._readonly:
            raise AttributeError("FldDataMemmap in read-only mode does not support field assignment.")
        if other.size != 0 and other.shape != (self.nelt, self.nx1 * self.ny1 * self.nz1,):
            raise ValueError("Incorrect shape for t: t.shape must equal ``(nelt * nx1 * ny1 * nz1,)``")
        self._t = other.astype(self.float_type)
        self._set_rdcode()

    @FldDataBase.s.setter
    def s(self, other: np.ndarray):
        if self._readonly:
            raise AttributeError("FldDataMemmap in read-only mode does not support field assignment.")
        if other.size != 0 and (
                len(other.shape) != 3 or other.shape[1:] != (self.nelt, self.nx1 * self.ny1 * self.nz1)):
            raise ValueError(
                "Incorrect shape for s: s.shape must equal (x, nelt, nx1 * ny1 * nz1) for arbitrary number of scalars x")
        self._s = other.astype(self.float_type)
        self._set_rdcode()
