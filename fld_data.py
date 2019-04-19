import numpy as np
import re
from fld_header import FldHeader
from typing import Tuple


class FldData:

    def __init__(self,
                 filename: str,
                 ndim: int,
                 nscalars: int,
                 header: FldHeader,
                 coords: np.array,
                 u: np.array,
                 p: np.array,
                 t: np.array,
                 s: np.array):
        self.filename = filename
        self.ndim = ndim
        self.nscalars = nscalars
        self._header = header
        self.coords = coords
        self.u = u
        self.p = p
        self.t = t
        self.s = s

    @classmethod
    def fromfile(cls, filename: str, ndim: int = 3):

        def notify(msg: str):
            print("[{}] : {}".format(filename, msg))

        def error(msg: str):
            raise Exception("[{}] : {}".format(filename, msg))

        h = FldHeader.fromfile(filename)

        nscalars = 0
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
                    size = ndim * h.nelt * h.nx1 * h.ny1 * h.nz1 * h.float_type.itemsize
                    coords = np.frombuffer(f.read(size), dtype=h.float_type).reshape(ndim, -1)

                # Velocity field
                elif code == 'U':
                    notify("Located velocity field U")
                    size = ndim * h.nelt * h.nx1 * h.ny1 * h.nz1 * h.float_type.itemsize
                    u = np.frombuffer(f.read(size), dtype=h.float_type).reshape(ndim, -1)

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
                        error("Couldn't parse number of passive scalar fields")
                    else:
                        notify("Located {} passive scalar fields".format(nscalars))
                        size = nscalars * h.nelt * h.nx1 * h.ny1 * h.nz1 * h.float_type.itemsize
                        s = np.frombuffer(f.read(size), dtype=h.float_type).reshape(nscalars, -1)

                else:
                    error("Warning: Unsupported rdcode '{}'".format(code))

        return cls(filename=filename, ndim=ndim, nscalars=nscalars, header=h, coords=coords, u=u, p=p, t=t, s=s)

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
        pass

    def tofile(self, filename):
        self._header.tofile(filename)
        with open(filename, 'ab') as f:
            f.write(self.coords.tobytes())
            f.write(self.u.tobytes())
            f.write(self.p.tobytes())
            f.write(self.t.tobytes())
            f.write(self.s.tobytes())

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        width = max(len(key) for key in self.__dict__)
        result = str(self._header)
        for k, v in self.__dict__.items():
            if k != '_header':
                result += '{key:{width}} = {value}\n'.format(key=k, value=v, width=width)
        return result

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


if __name__ == '__main__':
    ## Parses data from a test file, then prints data as plaintext files for inspection

    # fld = FldData('data/test0.f00001')

    # g = fld.get_glob_el_nums()
    # c = fld.get_coord()
    # v = fld.get_velocity()
    # p = fld.get_pressure()
    # t = fld.get_temperature()

    # with open('_header.txt', 'w') as f:
    #    print(fld._header, file=f)

    # with open('glob_el_nums.txt', 'w') as f:
    #    g.tofile(f, sep=' ', format='%3d')

    # with open('coords.txt', 'w') as f:
    #    fmt = '%.3e'
    #    for i in range(fld.ndim):
    #        c[i:].tofile(f, sep=' ', format=fmt)
    #        f.write('\n')

    fld = FldData.fromfile('data/test0.f00001')
    print(fld)

    test_outfile = 'fld_header_test.bin'
    fld.tofile(test_outfile)

    fld2 = FldData.fromfile(test_outfile)
    print('***************')
    print(fld2)
