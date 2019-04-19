import numpy as np
import re
from fld_header import FldHeader
from typing import Tuple


class FldReader:

    def __init__(self, filename: str, ndim: int = 3):

        self.filename = filename
        self.ndim = int(ndim)  # TODO: Check if this is consistent with nz ?
        self.nscalars = 0

        # Get header
        self.header = FldHeader.from_file(self.filename)

        # Fields will be empty until they are parsed below
        self.coords = np.array([])
        self.u = np.array([])
        self.p = np.array([])
        self.t = np.array([])
        self.s = np.array([])

        self._notify("Attempting to parse rdcode {}".format(self.rdcode))

        # Begin parsing fields after the header
        offset = 136 + self.nelt * self.int_type.itemsize

        # Parse rdcode into list (e.g., "XUS01" is parsed into ['X', 'U', 'S01']
        code_list = [s.upper() for s in re.split(r'(\D\d*)', self.rdcode) if s]

        for code in code_list:

            # Coordinate data
            if code == 'X':
                count = self.ndim * self.nelt * self.nx1 * self.ny1 * self.nz1
                self.coords = self._get_array(offset=offset, count=count, dtype=self.float_type,
                                              reshape=(self.ndim, -1))
                offset += count * self.float_type.itemsize
                self._notify("Located coordinates X")

            # Velocity field
            elif code == 'U':
                count = self.ndim * self.nelt * self.nx1 * self.ny1 * self.nz1
                self.u = self._get_array(offset=offset, count=count, dtype=self.float_type, reshape=(self.ndim, -1))
                offset += count * self.float_type.itemsize
                self._notify("Located velocity field U")

            # Pressure field
            elif code == 'P':
                count = self.nelt * self.nx1 * self.ny1 * self.nz1
                self.p = self._get_array(offset=offset, count=count, dtype=self.float_type)
                offset += count * self.float_type.itemsize
                self._notify("Located pressure field P")

            # Temperature field
            elif code == 'T':
                count = self.nelt * self.nx1 * self.ny1 * self.nz1
                self.t = self._get_array(offset=offset, count=count, dtype=self.float_type)
                offset += count * self.float_type.itemsize
                self._notify("Located temperature field T")

            # Passive scalars
            elif code.startswith('S'):
                try:
                    self.nscalars = int(code[1:])
                except ValueError:
                    self._notify(
                        "Warning: Couldn't parse number of passive scalar fields (attempted to parse code {})".format(
                            code))
                count = self.nscalars * self.nelt * self.nx1 * self.ny1 * self.nz1
                self.s = self._get_array(offset=offset, count=count, dtype=self.float_type, reshape=(self.nscalars, -1))
                offset += count * self.float_type.itemsize
                self._notify("Located {} passive scalar fields".format(self.nscalars))

            else:
                self._notify("Warning: Unsupported rdcode '{}'".format(code))

    def from_file(self, filename: str, ndim: int = 3):
        self.__init__(filename, ndim)

    def to_file(self, filename):
        self.header.to_file(filename)
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

    def _notify(self, msg: str):
        print("[{}] : {}".format(self.filename, msg))

    def _error(self, msg: str):
        raise Exception("[{}] : {}".format(self.filename, msg))

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        width = max(len(key) for key in self.__dict__)
        result = str(self.header)
        for k, v in self.__dict__.items():
            if k != 'header':
                result += '{key:{width}} = {value}\n'.format(key=k, value=v, width=width)
        return result

    @property
    def nx1(self) -> int:
        return self.header.nx1

    @property
    def ny1(self) -> int:
        return self.header.ny1

    @property
    def nz1(self) -> int:
        return self.header.nz1

    @property
    def nelt(self) -> int:
        return self.header.nelt

    @property
    def nelgt(self) -> int:
        return self.header.nelgt

    @property
    def time(self) -> float:
        return self.header.time

    @property
    def iostep(self) -> int:
        return self.header.iostep

    @property
    def fid0(self) -> int:
        return self.header.fid0

    @property
    def nfileoo(self) -> int:
        return self.header.nfileoo

    @property
    def rdcode(self) -> str:
        return self.header.rdcode

    @property
    def p0th(self) -> float:
        return self.header.p0th

    @property
    def if_press_mesh(self) -> bool:
        return self.header.if_press_mesh

    @property
    def float_type(self) -> np.dtype:
        return self.header.float_type

    @property
    def int_type(self) -> np.dtype:
        return self.header.int_type


if __name__ == '__main__':
    ## Parses data from a test file, then prints data as plaintext files for inspection

    # fld = FldReader('data/test0.f00001')

    # g = fld.get_glob_el_nums()
    # c = fld.get_coord()
    # v = fld.get_velocity()
    # p = fld.get_pressure()
    # t = fld.get_temperature()

    # with open('header.txt', 'w') as f:
    #    print(fld.header, file=f)

    # with open('glob_el_nums.txt', 'w') as f:
    #    g.tofile(f, sep=' ', format='%3d')

    # with open('coords.txt', 'w') as f:
    #    fmt = '%.3e'
    #    for i in range(fld.ndim):
    #        c[i:].tofile(f, sep=' ', format=fmt)
    #        f.write('\n')

    fld = FldReader('data/test0.f00001')
    print(fld)

    test_outfile = 'fld_header_test.bin'
    fld.to_file(test_outfile)

    fld2 = FldReader(test_outfile)
    print('***************')
    print(fld2)
