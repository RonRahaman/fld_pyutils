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

        self._notify("Attempting to parse rdcode {}".format(self.header.rdcode))

        # Begin parsing fields after the header
        offset = 136 + self.header.nelt * self.header.int_type.itemsize

        # Parse rdcode into list (e.g., "XUS01" is parsed into ['X', 'U', 'S01']
        code_list = [s.upper() for s in re.split(r'(\D\d*)', self.header.rdcode) if s]

        for code in code_list:

            # Coordinate data
            if code == 'X':
                count = self.ndim * self.header.nelt * self.header.nx1 * self.header.ny1 * self.header.nz1
                self.coords = self._get_array(offset=offset, count=count, dtype=self.header.float_type,
                                              reshape=(self.ndim, -1))
                offset += count * self.header.float_type.itemsize
                self._notify("Located coordinates X")

            # Velocity field
            elif code == 'U':
                count = self.ndim * self.header.nelt * self.header.nx1 * self.header.ny1 * self.header.nz1
                self.u = self._get_array(offset=offset, count=count, dtype=self.header.float_type,
                                         reshape=(self.ndim, -1))
                offset += count * self.header.float_type.itemsize
                self._notify("Located velocity field U")

            # Pressure field
            elif code == 'P':
                count = self.header.nelt * self.header.nx1 * self.header.ny1 * self.header.nz1
                self.p = self._get_array(offset=offset, count=count, dtype=self.header.float_type)
                offset += count * self.header.float_type.itemsize
                self._notify("Located pressure field P")

            # Temperature field
            elif code == 'T':
                count = self.header.nelt * self.header.nx1 * self.header.ny1 * self.header.nz1
                self.t = self._get_array(offset=offset, count=count, dtype=self.header.float_type)
                offset += count * self.header.float_type.itemsize
                self._notify("Located temperature field T")

            # Passive scalars
            elif code.startswith('S'):
                try:
                    self.nscalars = int(code[1:])
                except ValueError:
                    self._notify(
                        "Warning: Couldn't parse number of passive scalar fields (attempted to parse code {})".format(
                            code))
                count = self.nscalars * self.header.nelt * self.header.nx1 * self.header.ny1 * self.header.nz1
                self.s = self._get_array(offset=offset, count=count, dtype=self.header.float_type,
                                         reshape=(self.nscalars, -1))
                offset += count * self.header.float_type.itemsize
                self._notify("Located {} passive scalar fields".format(self.nscalars))

            else:
                self._notify("Warning: Unsupported rdcode '{}'".format(code))

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
    fld.header.to_file(test_outfile)

    fld2 = FldReader(test_outfile)
    print('***************')
    print(fld2)
