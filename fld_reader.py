import numpy as np


class FldData:
    """ Handles reading of Nek5000 fld file data.

    The header is always read and kept in memory.  The other the data (global element numbers and field data) are
    only parsed and returned when requested by get_glob_el_nums or get_field.

    Attributes:
        filename (string): Path to fld file
        ndim (int, optional): Number of dimensions in corresponding model.  Default: 3
        float_size (int): Size of floats (in bytes) used in the fld file
        nx (int):
        ny (int):
        nz (int):
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
        glob_el_nums_offset (int):  Bytes at which the global element numbers begin, counting from beginning of file
        field_offset (int):  Bytes at which the field data begin, counting from beginning of file
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
            self.nx = int(header_list[2])
            self.ny = int(header_list[3])
            self.nz = int(header_list[4])
            self.nelt = int(header_list[5])
            self.nelgt = int(header_list[6])
            self.time = float(header_list[7])
            self.iostep = int(header_list[8])
            self.fid0 = int(header_list[9])
            self.nfileoo = int(header_list[10])
            self.rdcode = header_list[11]
            self.p0th = float(header_list[12]),
            self.if_press_mesh = False if 'F' in header_list[13] else True

            # Get endian test value (should be 6.54321 if endianness matches this system's)
            endian_test_val = np.fromfile(f, dtype=np.float32, count=1)

            # Set float size based on what the fld file says.  Only 32 and 64 bit types are supported.
            if self.float_size == 4:
                self.float_type = np.dtype(np.float32)
            elif self.float_size == 8:
                self.float_type = np.dtype(np.float64)
            else:
                raise ValueError('{} specified invalid float size {}'.format(self.filename, self.float_size))

            # If necessary, switch endianness of float type
            if not np.all(np.isclose(endian_test_val, [6.54321], atol=1e-6, rtol=0.0)):
                self.float_type = self.float_type.newbyteorder('S')

            # Always set int size to int32
            self.int_type = np.dtype(np.int32)

        # Set offset locations of global element number and field data
        self.glob_el_nums_offset = 136
        self.field_offset = 136 + self.nelt

    def get_glob_el_nums(self):
        """ Get the array of global element numbers.

        Returns:
            np.array: An array of global element numbers.  Shape is [nelt,]
        """
        with open(self.filename, 'rb') as f:
            f.seek(self.glob_el_nums_offset)
            return np.fromfile(f, dtype=self.int_type, count=self.nelt)

    def get_field(self):
        """ Get the field data itself.

        Returns:
            np.array:  An array of field data.  Shape is [ndim, ndim*nx*ny*nz*nelt]
        """
        with open(self.filename, 'rb') as f:
            f.seek(self.field_offset)
            count = self.ndim * self.nx * self.ny * self.nz * self.nelt
            return np.fromfile(f, dtype=self.float_type, count=count).reshape([self.ndim, -1])

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

    with open('field.txt', 'w') as f:
        fmt = '%.3e'
        fld_array = fld.get_field()
        for i in range(fld.ndim):
            fld_array[i:].tofile(f, sep=' ', format=fmt)
            f.write('\n')
