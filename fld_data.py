import numpy as np
import re
from fld_header import FldHeader


class FldData:

    def __init__(self,
                 header: FldHeader,
                 coords: np.array = None,
                 u: np.array = None,
                 p: np.array = None,
                 t: np.array = None,
                 s: np.array = None):

        self._header = header

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
                    size = h.ndims * h.nelt * h.nx1 * h.ny1 * h.nz1 * h.float_type.itemsize
                    coords = np.frombuffer(f.read(size), dtype=h.float_type).reshape(h.ndims, -1)

                # Velocity field
                elif code == 'U':
                    notify("Located velocity field U")
                    size = h.ndims * h.nelt * h.nx1 * h.ny1 * h.nz1 * h.float_type.itemsize
                    u = np.frombuffer(f.read(size), dtype=h.float_type).reshape(h.ndims, -1)

                # Pressure field
                elif code == 'P':
                    notify("Located pressure field P")
                    size = h.nelt * h.nx1 * h.ny1 * h.nz1 * h.float_type.itemsize
                    p = np.frombuffer(f.read(size), dtype=h.float_type)

                # Temperature field
                elif code == 'T':
                    notify("Located temperature field T")
                    size = h.nelt * h.nx1 * h.ny1 * h.nz1 * h.float_type.itemsize
                    t = np.frombuffer(f.read(size), dtype=h.float_type)

                # Passive scalars
                elif code.startswith('S'):
                    try:
                        nscalars = int(code[1:])
                    except ValueError:
                        error("Couldn'_t parse number of passive scalar fields")
                    else:
                        notify("Located {} passive scalar fields".format(nscalars))
                        size = nscalars * h.nelt * h.nx1 * h.ny1 * h.nz1 * h.float_type.itemsize
                        s = np.frombuffer(f.read(size), dtype=h.float_type).reshape(nscalars, -1)

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
                   glel: np.array = None,
                   coords: np.array = None,
                   u: np.array = None,
                   p: np.array = None,
                   t: np.array = None,
                   s: np.array = None):

        header = FldHeader(nelgt=nelgt, nx1=nx1, ny1=ny1, nz1=nz1, nelt=nelt, time=time, iostep=iostep, fid0=fid0,
                           nfileoo=nfileoo, p0th=p0th, if_press_mesh=if_press_mesh, float_type=float_type,
                           int_type=int_type, glel=glel)

        return cls(header=header, coords=coords, u=u, p=p, t=t, s=s)

    def tofile(self, filename):
        self._header.tofile(filename)
        with open(filename, 'ab') as f:
            f.write(self._coords.tobytes())
            f.write(self._u.tobytes())
            f.write(self._p.tobytes())
            f.write(self._t.tobytes())
            f.write(self._s.tobytes())

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        attr = dict(coords=self.coords, u=self.u, p=self.p, t=self.t, s=self.s)
        result = str(self._header)
        for k, v in attr.items():
            result += '{key} =\n{value}\n'.format(key=k, value=v)
        return result

    def _set_rdcode(self):
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
            rdcode += "S{:2}".format(self.nscalars)
        self._header.rdcode = rdcode

    @property
    def nx1(self) -> int:
        return self._header.nx1

    @property
    def ny1(self) -> int:
        return self._header.ny1

    @property
    def nz1(self) -> int:
        return self._header.nz1

    @property
    def nelt(self) -> int:
        return self._header.nelt

    @property
    def nelgt(self) -> int:
        return self._header.nelgt

    @property
    def time(self) -> float:
        return self._header.time

    @property
    def iostep(self) -> int:
        return self._header.iostep

    @property
    def fid0(self) -> int:
        return self._header.fid0

    @property
    def nfileoo(self) -> int:
        return self._header.nfileoo

    @property
    def rdcode(self) -> str:
        return self._header.rdcode

    @property
    def p0th(self) -> float:
        return self._header.p0th

    @property
    def if_press_mesh(self) -> bool:
        return self._header.if_press_mesh

    @property
    def float_type(self) -> np.dtype:
        return self._header.float_type

    @property
    def int_type(self) -> np.dtype:
        return self._header.int_type

    @property
    def glel(self) -> np.array:
        return self._header.glel

    @glel.setter
    def glel(self, other: np.array):
        # glel is a managed attribute of FldHeader, so no need to validate it here in FldData
        self._header.glel = other

    @property
    def ndims(self) -> int:
        return self._header.ndims

    @property
    def nscalars(self):
        return self._header.nscalars

    @property
    def coords(self) -> np.array:
        return self._coords

    @coords.setter
    def coords(self, other: np.array):
        if other.size != 0 and other.shape != (self.ndims, self.nelt * self.nx1 * self.ny1 * self.nz1):
            raise ValueError("Incorrect shape for coords: coords.shape must equal (ndims, nelt * nx1 * ny1 * nz1)")
        self._coords = other.astype(self.float_type)
        self._set_rdcode()

    @property
    def u(self) -> np.array:
        return self._u

    @u.setter
    def u(self, other: np.array):
        if other.size != 0 and other.shape != (self.ndims, self.nelt * self.nx1 * self.ny1 * self.nz1):
            raise ValueError("Incorrect shape for u: u.shape must equal (ndims, nelt * nx1 * ny1 * nz1)")
        self._u = other.astype(self.float_type)
        self._set_rdcode()

    @property
    def p(self) -> np.array:
        return self._p

    @p.setter
    def p(self, other: np.array):
        if other.size != 0 and other.shape != (self.nelt * self.nx1 * self.ny1 * self.nz1,):
            raise ValueError("Incorrect shape for p: p.shape must equal (nelt * nx1 * ny1 * nz1,)")
        self._p = other.astype(self.float_type)
        self._set_rdcode()

    @property
    def t(self) -> np.array:
        return self._t

    @t.setter
    def t(self, other: np.array):
        if other.size != 0 and other.shape != (self.nelt * self.nx1 * self.ny1 * self.nz1,):
            raise ValueError("Incorrect shape for t: t.shape must equal (nelt * nx1 * ny1 * nz1,)")
        self._t = other.astype(self.float_type)
        self._set_rdcode()

    @property
    def s(self):
        return self._s

    @s.setter
    def s(self, other: np.array):
        if other.size != 0 and other.shape != (self.nscalars, self.nelt * self.nx1 * self.ny1 * self.nz1):
            raise ValueError("Incorrect shape for _s: _s.shape must equal (nscalars, nelt * nx1 * ny1 * nz1)")
        self._s = other.astype(self.float_type)
        self._nscalars = other.shape[0]
        self._set_rdcode()


if __name__ == '__main__':
    # Test 1:  Parses a file, writes it to a second file, then parses the second file
    # ===============================================================================

    fld = FldData.fromfile('data/test0.f00001')
    print(fld)

    print('***************')

    test_outfile = 'fld_header_test.bin'
    fld.tofile(test_outfile)
    fld2 = FldData.fromfile(test_outfile)
    print(fld2)

    # Test 2: Creates a file from values, writes it to a file, then parses it again
    # ===============================================================================

    # # Required
    # ndims = 3
    # nx1 = 7
    # ny1 = nx1
    # nz1 = nx1
    # nelgt = 512
    # nelt = nelgt
    # float_type = np.dtype(np.float32)
    # int_type = np.dtype(np.int32)

    # # Optional
    # glel = np.arange(1, nelt + 1)
    # coords = np.vstack((np.full(nelt * nx1 ** 3, fill_value=2),
    #                     np.full(nelt * nx1 ** 3, fill_value=3),
    #                     np.full(nelt * nx1 ** 3, fill_value=4)))
    # u = np.vstack((np.full(nelt * nx1 ** 3, fill_value=5),
    #                np.full(nelt * nx1 ** 3, fill_value=6),
    #                np.full(nelt * nx1 ** 3, fill_value=7)))
    # p = np.full(nelt * nx1 ** 3, fill_value=8)
    # t = np.full(nelt * nx1 ** 3, fill_value=9)

    # fld = FldData.fromvalues(nx1=nx1, ny1=ny1, nz1=nz1, nelgt=nelgt, nelt=nelt,
    #                          glel=glel, coords=coords, u=u, p=p, t=t)
    # print(fld)

    # # print('***************')

    # test_outfile = 'fld_header_test.bin'
    # fld.tofile(test_outfile)

    # fld2 = FldData.fromfile(test_outfile)
    # print(fld2)
