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

        res = cls(filename=filename,
                  ndim=ndim,
                  nscalars=0,
                  header=FldHeader.fromfile(filename),
                  coords=np.array([]),
                  u=np.array([]),
                  p=np.array([]),
                  t=np.array([]),
                  s=np.array([]))

        notify("Attempting to parse rdcode {}".format(res.rdcode))

        # Begin parsing fields after the _header
        offset = 136 + res.nelt * res.int_type.itemsize

        # Parse rdcode into list (e.g., "XUS01" is parsed into ['X', 'U', 'S01']
        code_list = [s.upper() for s in re.split(r'(\D\d*)', res.rdcode) if s]

        for code in code_list:

            # Coordinate data
            if code == 'X':
                count = res.ndim * res.nelt * res.nx1 * res.ny1 * res.nz1
                res.coords = res._get_array(offset=offset, count=count, dtype=res.float_type, reshape=(res.ndim, -1))
                offset += count * res.float_type.itemsize
                notify("Located coordinates X")

            # Velocity field
            elif code == 'U':
                count = res.ndim * res.nelt * res.nx1 * res.ny1 * res.nz1
                res.u = res._get_array(offset=offset, count=count, dtype=res.float_type, reshape=(res.ndim, -1))
                offset += count * res.float_type.itemsize
                notify("Located velocity field U")

            # Pressure field
            elif code == 'P':
                count = res.nelt * res.nx1 * res.ny1 * res.nz1
                res.p = res._get_array(offset=offset, count=count, dtype=res.float_type)
                offset += count * res.float_type.itemsize
                notify("Located pressure field P")

            # Temperature field
            elif code == 'T':
                count = res.nelt * res.nx1 * res.ny1 * res.nz1
                res.t = res._get_array(offset=offset, count=count, dtype=res.float_type)
                offset += count * res.float_type.itemsize
                notify("Located temperature field T")

            # Passive scalars
            elif code.startswith('S'):
                try:
                    res.nscalars = int(code[1:])
                except ValueError:
                    notify(
                        "Warning: Couldn't parse number of passive scalar fields (attempted to parse code {})".format(
                            code))
                count = res.nscalars * res.nelt * res.nx1 * res.ny1 * res.nz1
                res.s = res._get_array(offset=offset, count=count, dtype=res.float_type, reshape=(res.nscalars, -1))
                offset += count * res.float_type.itemsize
                notify("Located {} passive scalar fields".format(res.nscalars))

            else:
                error("Warning: Unsupported rdcode '{}'".format(code))

        return res

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

    def _get_array(self, offset: int, dtype: np.dtype, count: int, reshape: Tuple = None) -> np.array:
        with open(self.filename, 'rb') as f:
            f.seek(offset)
            array = np.fromfile(f, dtype=dtype, count=count)
            if reshape:
                return array.reshape(reshape)
            else:
                return array

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
