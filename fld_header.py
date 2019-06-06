import numpy as np
from re import search


class FldHeader:
    """ Contains the header of a binary Nek5000 field file

    The constructor is typically not used directly.  Most users will prefer to use :py:meth:`FldHeader.fromfile` or
    :py:meth:`FldHeader.fromvalues`.


    Parameters
    ----------
    nelgt
        Number of global elements
    nx1
        Number of GLL gridpoints along x-axis
    ny1
        Number of GLL gridpoints along y-axis
    nz1
        Number of GLL gridpoints along z-axis
    nelt
        Number of elements in this file
    rdcode
        String representing the fields contained in this file
    time
        Absolute simulation time of this file's state
    iostep
        I/O timestep of this file's state
    fid0
        Index of this file, with respect to all files produced at this I/O step
    nfileoo
        Number of files produced at this I/O step
    p0th
        __
    if_press_mesh
        States whether pressure mesh is being used
    float_type
        Data type used for floating point numbers in this file
    int_type
        Data type used for integers in this file
    glel
        Array of global element indices; shape must be ``(nelt,)``
    """

    _endian_check_val = 6.54321

    def __init__(self,
                 nelgt: int,
                 nx1: int,
                 ny1: int,
                 nz1: int,
                 nelt: int = None,
                 rdcode: str = "",
                 time: float = 0.0,
                 iostep: int = 0,
                 fid0: int = 0,
                 nfileoo: int = 1,
                 p0th: float = 0.0,
                 if_press_mesh: bool = False,
                 float_type: np.dtype = np.dtype(np.float32),
                 int_type: np.dtype = np.dtype(np.int32),
                 glel: np.ndarray = None):
        self.nx1 = nx1
        self.ny1 = ny1
        self.nz1 = nz1
        self.nelt = nelt
        self.nelgt = nelgt
        self.time = time
        self.iostep = iostep
        self.fid0 = fid0
        self.nfileoo = nfileoo
        self.rdcode = rdcode
        self.p0th = p0th
        self.if_press_mesh = if_press_mesh
        self.float_type = float_type
        self.int_type = int_type

        if glel is None:
            glel = np.arange(1, nelt + 1, dtype=int_type)

        self.glel = glel

    @classmethod
    def fromfile(cls, filename: str):
        """ Creates a :py:class:`FldHeader` object from the contents of a given field file

        Parameters
        ----------
        filename
            Path to a binary Nek5000 field file

        Returns
        -------
        FldHeader
            A new instance of  :py:class:`FldHeader`

        """

        with open(filename, 'rb') as f:

            # Parse ASCII-formatted fields
            header_str = f.read(132).decode(encoding='ascii')
            header_list = header_str.split()

            float_size = int(header_list[1])  # always 32-bit
            nx1 = int(header_list[2])  # inferred from data
            ny1 = int(header_list[3])  # necessarily == nx1
            nz1 = int(header_list[4])  # inferred from data
            nelt = int(header_list[5])  # default to nelgt
            nelgt = int(header_list[6])  # inferred from data
            time = float(header_list[7])  # default = 0
            iostep = int(header_list[8])  # default = 0
            fid0 = int(header_list[9])  # file id, default = 0
            nfileoo = int(header_list[10])  # default = 1
            rdcode = header_list[11]  # infer from data
            p0th = float(header_list[12])  # default = 0

            # Set if_press_mesh               # default = F
            if header_list[13].casefold() == 'f':
                if_press_mesh = False
            elif header_list[13].casefold() == '_t':
                raise ValueError("{} specifies if_press_mesh='{}', but PnPn-2 is not supported for {}".format(
                    filename, header_list[13], cls.__name__))
            else:
                raise ValueError(
                    "{} contains if_press_mesh={}', which is not supported (only 'T' or 'F' supported)".format(
                        filename, header_list[13]))

            # Set float size based on what the fld file says.  Only 32 and 64 bit types are supported.
            if float_size == 4:
                float_type = np.dtype(np.float32)
            elif float_size == 8:
                float_type = np.dtype(np.float64)
            else:
                raise ValueError('{} specified invalid float size {}'.format(filename, float_size))

            # Get endian test value (should be 6.54321 if endianness matches this system'_s)
            # If necessary, switch endianness of float type
            endian_test_val = np.fromfile(f, dtype=np.float32, count=1)[0]
            if np.abs(endian_test_val - cls._endian_check_val) > 1e-6:
                float_type = float_type.newbyteorder('S')

            # Always set int size to int32
            int_type = np.dtype(np.int32)

            # Get global element list
            f.seek(136)
            glel = np.fromfile(f, dtype=int_type, count=nelt)

        return cls(nx1=nx1, ny1=ny1, nz1=nz1, nelt=nelt, nelgt=nelgt, rdcode=rdcode, time=time, iostep=iostep,
                   fid0=fid0, nfileoo=nfileoo, p0th=p0th, if_press_mesh=if_press_mesh, float_type=float_type,
                   int_type=int_type, glel=glel)

    @classmethod
    def fromvalues(cls,
                   nelgt: int,
                   nx1: int,
                   ny1: int,
                   nz1: int,
                   nelt: int = None,
                   rdcode: str = "",
                   time: float = 0.0,
                   iostep: int = 0,
                   fid0: int = 0,
                   nfileoo: int = 1,
                   p0th: float = 0.0,
                   if_press_mesh: bool = False,
                   float_type: np.dtype = np.dtype(np.float32),
                   int_type: np.dtype = np.dtype(np.int32),
                   glel: np.array = None):
        """ Creates a :py:class:`FldHeader` object from the given data values

        Parameters
        ----------
        nelgt
            Number of global elements
        nx1
            Number of GLL gridpoints along x-axis
        ny1
            Number of GLL gridpoints along y-axis
        nz1
            Number of GLL gridpoints along z-axis
        nelt
            Number of elements in this file
        rdcode
            String representing the fields contained in this file
        time
            Absolute simulation time of this file's state
        iostep
            I/O timestep of this file's state
        fid0
            Index of this file, with respect to all files produced at this I/O step
        nfileoo
            Number of files produced at this I/O step
        p0th
            __
        if_press_mesh
            States whether pressure mesh is being used
        float_type
            Data type used for floating point numbers in this file
        int_type
            Data type used for integers in this file
        glel
            Array of global element indices; shape must be ``(nelt,)``

        Returns
        -------
        FldHeader
            A new instance of  :py:class:`FldHeader`

        """


        return cls(nx1=nx1, ny1=ny1, nz1=nz1, nelt=nelt, nelgt=nelgt, rdcode=rdcode, time=time, iostep=iostep,
                   fid0=fid0, nfileoo=nfileoo, p0th=p0th, if_press_mesh=if_press_mesh, float_type=float_type,
                   int_type=int_type, glel=glel)

    def tofile(self, filename: str):

        wdsize = self.float_type.itemsize
        press_mesh = '_t' if self.if_press_mesh else 'f'

        fmt = '#std {wdsize:1d} {nx1:2d} {ny1:2d} {nz1:2d} {nelt:10d} {nelgt:10d} {time:20.13e} {iostep:9d} ' + \
              '{fid0:6d} {nfileoo:6d} {rdcode:10} {p0th:15.7e} {press_mesh:1}'
        header_text = fmt.format(**self.__dict__, wdsize=wdsize, press_mesh=press_mesh)

        with open(filename, 'wb') as f:
            f.write(header_text.encode('ascii'))
            blanks = " " * (132 - f.tell())
            f.write(blanks.encode('ascii'))
            f.write(np.array([self.__class__._endian_check_val], dtype=self.float_type).tobytes())
            f.write(self.glel.tobytes())

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        attr = self.__dict__.copy()
        del attr['_glel']
        attr['ndims'] = self.ndims
        attr['nscalars'] = self.nscalars

        width = max(len(key) for key in attr)

        result = ''
        for k, v in attr.items():
            result += '{key:{width}} = {value}\n'.format(key=k, value=v, width=width)

        result += '{key} =\n{value}\n'.format(key='glel', value=self.glel)

        return result

    @property
    def glel(self) -> np.ndarray:
        """ Array of global element indices; shape is ``(nelt,)`` """
        return self._glel

    @glel.setter
    def glel(self, other: np.ndarray):
        if other.shape != (self.nelt,):
            raise ValueError("Incorrect shape for glel: glel.shape must equal (nelt,)")
        self._glel = other.astype(self.int_type)

    @property
    def ndims(self) -> int:
        """ Number of physical dimensions in this simulation """
        return 2 if self.nz1 == 1 else 3

    @property
    def nscalars(self) -> int:
        """ Number of passive scalars """
        res = search(r'S(\d+)', self.rdcode)
        return int(res.group(1)) if res else 0
