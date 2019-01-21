import numpy as np
import re


class FldData:
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

        # TODO: Check if this is consistent with nz ?
        self.ndim = int(ndim)

        with open(self.filename, 'rb') as f:

            # Parse ASCII-formatted fields
            header_str = f.read(132).decode(encoding='ascii')
            header_list = header_str.split()

            self.float_size = int(header_list[1])
            self.nx1 = int(header_list[2])
            self.ny1 = int(header_list[3])
            self.nz1 = int(header_list[4])
            self.nelt = int(header_list[5])
            self.nelgt = int(header_list[6])
            self.time = float(header_list[7])
            self.iostep = int(header_list[8])
            self.fid0 = int(header_list[9])
            self.nfileoo = int(header_list[10])
            self.rdcode = header_list[11]
            self.p0th = float(header_list[12]),

            # Set if_press_mesh
            if header_list[13].casefold() == 'f':
                self.if_press_mesh = False
            elif header_list[13].casefold() == 't':
                raise ValueError("{} specifies if_press_mesh='{}', but PnPn-2 is not supported for {}".format(
                    self.filename, header_list[13], self.__class__.__name__))
            else:
                raise ValueError(
                    "{} contains if_press_mesh={}', which is not supported (only 'T' or 'F' supported)".format(
                        self.filename, header_list[13]))

            # Set float size based on what the fld file says.  Only 32 and 64 bit types are supported.
            if self.float_size == 4:
                self.float_type = np.dtype(np.float32)
            elif self.float_size == 8:
                self.float_type = np.dtype(np.float64)
            else:
                raise ValueError('{} specified invalid float size {}'.format(self.filename, self.float_size))

            # Get endian test value (should be 6.54321 if endianness matches this system's)
            # If necessary, switch endianness of float type
            endian_test_val = np.fromfile(f, dtype=np.float32, count=1)[0]
            if np.abs(endian_test_val - 6.54321) > 1e-6:
                self.float_type = self.float_type.newbyteorder('S')

            # Always set int size to int32
            self.int_type = np.dtype(np.int32)

        # Set offset locations of global element number (always present)
        self._glob_el_offset = 136
        self._glob_el_count = self.nelt

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

        current_offset = self._glob_el_offset + self._glob_el_count * self.int_type.itemsize

        self._notify("Attempting to parse rdcode {}".format(self.rdcode))

        # Parse something like "XUS01" into ['X', 'U', 'S01']
        code_list = [s.upper() for s in re.split(r'(?!\d)', self.rdcode) if s]
        for code in code_list:

            # Coordinate data
            if code == 'X':
                self._coord_count = self.ndim * self.nx1 * self.ny1 * self.nz1 * self.nelt
                self._coord_offset = current_offset
                current_offset += self._coord_count * self.float_type.itemsize
                self._notify("Located coorinates X")

            # Velocity field
            elif code == 'U':
                self._velocity_count = self.ndim * self.nx1 * self.ny1 * self.nz1 * self.nelt
                self._velocity_offset = current_offset
                current_offset += self._velocity_count * self.float_type.itemsize
                self._notify("Located velocity field U")

            # Pressure field
            elif code == 'P':
                self._pressure_count = self.nx1 * self.ny1 * self.nz1 * self.nelt
                self._pressure_offset = current_offset
                current_offset += self._pressure_count * self.float_type.itemsize
                self._notify("Located pressure field P")

            # Temperature field
            elif code == 'T':
                self._temperature_count = self.nx1 * self.ny1 * self.nz1 * self.nelt
                self._temperature_offset = current_offset
                current_offset += self._temperature_count * self.float_type.itemsize
                self._notify("Located temperature field T")

            # Passive scalars
            # TODO: The passive scalars will be 0-based indexed once we parse them.  Maybe use dicts
            elif code.startswith('S'):
                try:
                    num_scalars = int(code[1:])
                except ValueError:
                    self._notify(
                        "Warning: Couldn't parse number of passive scalar fields (attempted to parse code {})".format(
                            code))
                else:
                    for i in range(1, num_scalars + 1):
                        self._passive_scalar_counts[i] = self.nx1 * self.ny1 * self.nz1 * self.nelt
                        self._passive_scalar_offsets[i] = current_offset
                        current_offset += self._passive_scalar_counts[i] * self.float_type.itemsize
                    self._notify("Located {} passive scalar fields from {}".format(num_scalars, code))

            else:
                self._notify("Warning: Unsupported rdcode '{'".format(code))

    def get_glob_el_nums(self):
        """ Get the array of global element numbers.

        Returns:
            np.array: An array of global element numbers.  Shape is [nelt,]
        """
        return self._get_array(offset=self._glob_el_offset, count=self._glob_el_count, dtype=self.int_type)

    def get_coordinates(self):
        """ Get the coordinates

        Returns:
            np.array:  An array of coordinates.  Shape is [ndim, ndim*nx*ny*nz*nelt]
        """
        if self._coord_count:
            return self._get_array(offset=self._coord_offset, count=self._coord_count, dtype=self.float_type,
                                   reshape=[self.ndim, -1])
        else:
            self._error("No coordinate field was found.")

    def _get_array(self, offset, dtype, count, reshape=None):
        with open(self.filename, 'rb') as f:
            f.seek(offset)
            array = np.fromfile(f, dtype=dtype, count=count)
            if reshape:
                return array.reshape(reshape)
            else:
                return array

    def _notify(self, msg):
        print("[{}] : {}".format(self.filename, msg))

    def _error(self, error, msg):
        raise error("[{}] : {}".format(self.filename, msg))

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        width = max(len(key) for key in self.__dict__)
        result = ''
        for k, v in self.__dict__.items():
            result += '{key:{width}} = {value}\n'.format(key=k, value=v, width=width)
        return result


if __name__ == '__main__':

    # Parses data from a test file, then prints data as plaintext files for inspection

    fld = FldData('data/test0.f00001')

    with open('header.txt', 'w') as f:
        print(fld, file=f)

    with open('glob_el_nums.txt', 'w') as f:
        glob_el_array = fld.get_glob_el_nums()
        glob_el_array.tofile(f, sep=' ', format='%3d')

    with open('coords.txt', 'w') as f:
        fmt = '%.3e'
        fld_array = fld.get_coordinates()
        for i in range(fld.ndim):
            fld_array[i:].tofile(f, sep=' ', format=fmt)
            f.write('\n')
