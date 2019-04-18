import numpy as np
import re
from fld_header import FldHeader
from typing import Tuple


class FldReader:
    """ Handles reading of Nek5000 fld file data.

    The header is always read and kept in memory.  The other the data (global element numbers and field data) are
    only parsed and returned when requested by get_glob_el_nums or get_field.

    Attributes:
        filename (string): Path to fld file
        ndim (int, optional): Number of dimensions in corresponding model.  Default: 3
        float_size (int): Size of floats (in bytes) used in the fld file
        nx1 (int):
        ny1 (int):
        nz1 (int):
        nelt (int):
        nelgt (int):
        time (float):
        iostep (int):
        fid0 (int):
        nfileoo (int):
        rdcode (str):
        p0th (float):
        if_press_mesh (bool):
        float_type (np.dtype):  Set to float32 or float64, depending on float_size.
            Endianness is determined from fld file.
        int_type (np.dtype):  Always set to int32.  Endianness is determined from fld file.
    """

    def __init__(self, filename, ndim=3):
        """ Parses header of given fld file.

        Args:
            filename (str): A path to the fld file
            ndim (str):  The number of dimensions in the corresponding model
        """

        self.filename = filename
        self.ndim = int(ndim)  # TODO: Check if this is consistent with nz ?

        # Get header
        self.header = FldHeader.from_file(self.filename)

        # Set offset locations of global element number (always present)
        self._glob_el_offset = 136
        self._glob_el_count = self.header.nelt

        self._coord_offset = None
        self._coord_count = None

        self._velocity_offset = None
        self._velocity_count = None

        self._pressure_offset = None
        self._pressure_count = None

        self._temperature_offset = None
        self._temperature_count = None

        self._passive_scalar_offsets = dict()
        self._passive_scalar_counts = dict()

        current_offset = self._glob_el_offset + self._glob_el_count * self.header.int_type.itemsize

        self._notify("Attempting to parse rdcode {}".format(self.header.rdcode))

        n_xyze = self.header.nx1 * self.header.ny1 * self.header.nz1 * self.header.nelt

        # Parse something like "XUS01" into ['X', 'U', 'S01']
        code_list = [s.upper() for s in re.split(r'(\D\d*)', self.header.rdcode) if s]
        for code in code_list:

            # Coordinate data
            if code == 'X':
                self._coord_count = self.ndim * n_xyze
                self._coord_offset = current_offset
                current_offset += self._coord_count * self.header.float_type.itemsize
                self._notify("Located coorinates X")

            # Velocity field
            elif code == 'U':
                self._velocity_count = self.ndim * n_xyze
                self._velocity_offset = current_offset
                current_offset += self._velocity_count * self.header.float_type.itemsize
                self._notify("Located velocity field U")

            # Pressure field
            elif code == 'P':
                self._pressure_count = n_xyze
                self._pressure_offset = current_offset
                current_offset += self._pressure_count * self.header.float_type.itemsize
                self._notify("Located pressure field P")

            # Temperature field
            elif code == 'T':
                self._temperature_count = n_xyze
                self._temperature_offset = current_offset
                current_offset += self._temperature_count * self.header.float_type.itemsize
                self._notify("Located temperature field T")

            # Passive scalars
            elif code.startswith('S'):
                try:
                    num_scalars = int(code[1:])
                except ValueError:
                    self._notify(
                        "Warning: Couldn't parse number of passive scalar fields (attempted to parse code {})".format(
                            code))
                else:
                    for i in range(1, num_scalars + 1):
                        self._passive_scalar_counts[i] = n_xyze
                        self._passive_scalar_offsets[i] = current_offset
                        current_offset += self._passive_scalar_counts[i] * self.header.float_type.itemsize
                    self._notify("Located {} passive scalar fields from {}".format(num_scalars, code))

            else:
                self._notify("Warning: Unsupported rdcode '{'".format(code))

    def get_glob_el_nums(self) -> np.array:
        """ Get the array of global element numbers.

        Returns:
            np.array: An array of global element numbers.  Shape is [nelt,]
        """
        return self._get_array(offset=self._glob_el_offset, count=self._glob_el_count, dtype=self.header.int_type)

    def get_coordinates(self) -> np.array:
        if self._coord_count:
            return self._get_array(offset=self._coord_offset, count=self._coord_count, dtype=self.header.float_type,
                                   reshape=(self.ndim, -1))
        else:
            self._error("No coordinate field was found.")

    def get_velocity(self) -> np.array:
        if self._velocity_count:
            return self._get_array(offset=self._velocity_offset, count=self._velocity_count, dtype=self.header.float_type,
                                   reshape=(self.ndim, -1))
        else:
            self._error("No velocity field was found.")

    def get_pressure(self) -> np.array:
        if self._pressure_count:
            return self._get_array(offset=self._pressure_offset, count=self._pressure_count, dtype=self.header.float_type)
        else:
            self._error("No pressure field was found.")

    def get_temperature(self) -> np.array:
        if self._temperature_count:
            return self._get_array(offset=self._temperature_offset, count=self._temperature_count, dtype=self.header.float_type)
        else:
            self._error("No temperature field was found.")

    def get_passive_scalar(self, n: int) -> np.array:
        if n in self._passive_scalar_counts:
            return self._get_array(offset=self._passive_scalar_offsets[n], count=self._passive_scalar_counts[n], dtype=self.header.float_type)
        else:
            self._error("Passive scalar {} was not found.".format(n))

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
        result = ''
        for k, v in self.__dict__.items():
            result += '{key:{width}} = {value}\n'.format(key=k, value=v, width=width)
        return result


if __name__ == '__main__':

    ## Parses data from a test file, then prints data as plaintext files for inspection

    #fld = FldReader('data/test0.f00001')

    #g = fld.get_glob_el_nums()
    #c = fld.get_coordinates()
    #v = fld.get_velocity()
    #p = fld.get_pressure()
    #t = fld.get_temperature()

    #with open('header.txt', 'w') as f:
    #    print(fld.header, file=f)

    #with open('glob_el_nums.txt', 'w') as f:
    #    g.tofile(f, sep=' ', format='%3d')

    #with open('coords.txt', 'w') as f:
    #    fmt = '%.3e'
    #    for i in range(fld.ndim):
    #        c[i:].tofile(f, sep=' ', format=fmt)
    #        f.write('\n')

    fld = FldReader('data/test0.f00001')
    print(fld.header)

    test_outfile = 'fld_header_test.bin'
    fld.header.to_file(test_outfile)

    fld2 = FldReader(test_outfile)
    print('***************')
    print(fld2.header)

