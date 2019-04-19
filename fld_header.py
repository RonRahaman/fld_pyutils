import numpy as np
from typing import Tuple


class FldHeader:
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
                 glel: np.array = None):
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
            self.glel = np.arange(1, nelt + 1, dtype=int_type)
        else:
            if nelt != glel.size:
                raise ValueError("Incorrect size of glel: nelt must be equal to glel.size")
            self.glel = np.array(glel, dtype=int_type)

    @classmethod
    def fromfile(cls, filename: str):

        with open(filename, 'rb') as f:

            # Parse ASCII-formatted fields
            header_str = f.read(132).decode(encoding='ascii')
            header_list = header_str.split()

            float_size = int(header_list[1])  # always 32-bit
            nx1 = int(header_list[2])         # inferred from data
            ny1 = int(header_list[3])         # necessarily == nx1
            nz1 = int(header_list[4])         # inferred from data
            nelt = int(header_list[5])        # default to nelgt
            nelgt = int(header_list[6])       # inferred from data
            time = float(header_list[7])      # default = 0
            iostep = int(header_list[8])      # default = 0
            fid0 = int(header_list[9])        # file id, default = 0
            nfileoo = int(header_list[10])    # default = 1
            rdcode = header_list[11]          # infer from data
            p0th = float(header_list[12])     # default = 0

            # Set if_press_mesh               # default = F
            if header_list[13].casefold() == 'f':
                if_press_mesh = False
            elif header_list[13].casefold() == 't':
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

            # Get endian test value (should be 6.54321 if endianness matches this system's)
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

        return cls(nx1=nx1, ny1=ny1, nz1=nz1, nelt=nelt, nelgt=nelgt, rdcode=rdcode, time=time, iostep=iostep,
                   fid0=fid0, nfileoo=nfileoo, p0th=p0th, if_press_mesh=if_press_mesh, float_type=float_type,
                   int_type=int_type, glel=glel)

    def tofile(self, filename: str):

        wdsize = self.float_type.itemsize
        press_mesh = 't' if self.if_press_mesh else 'f'

        fmt = '#std {wdsize:1d} {nx1:2d} {ny1:2d} {nz1:2d} {nelt:10d} {nelgt:10d} {time:20.13e} {iostep:9d} ' + \
              '{fid0:6d} {nfileoo:6d} {rdcode:10} {p0th:15.7e} {press_mesh:1}'
        header_text = fmt.format(**self.__dict__, **vars())

        with open(filename, 'wb') as f:
            f.write(header_text.encode('ascii'))
            blanks = " " * (132 - f.tell())
            f.write(blanks.encode('ascii'))
            f.write(np.array([self.__class__._endian_check_val], dtype=self.float_type).tobytes())
            f.write(self.glel.tobytes())

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        width = max(len(key) for key in self.__dict__)
        result = ''
        for k, v in self.__dict__.items():
            result += '{key:{width}} = {value}\n'.format(key=k, value=v, width=width)
        return result
