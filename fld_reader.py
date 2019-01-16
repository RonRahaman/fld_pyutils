import struct
import numpy as np
from collections import namedtuple

HeaderInfo = namedtuple('HeaderInfo', [
    'float_size',
    'nx',
    'ny',
    'nz',
    'nelt',
    'nelgt',
    'time',
    'iostep',
    'fid0',
    'nfileoo',
    'rdcode',
    'p0th',
    'if_press_mesh',
    'float_fmt',
    'int_size',
    'int_fmt'])

with open('data/test0.f00001', 'rb') as f:
    header = f.read(132).decode(encoding='ascii')
    header_list = header.split()

    hinfo = HeaderInfo(
        float_size=int(header_list[1]),
        nx=int(header_list[2]),
        ny=int(header_list[3]),
        nz=int(header_list[4]),
        nelt=int(header_list[5]),
        nelgt=int(header_list[6]),
        time=float(header_list[7]),
        iostep=int(header_list[8]),
        fid0=int(header_list[9]),
        nfileoo=int(header_list[10]),
        rdcode=header_list[11],
        p0th=float(header_list[12]),
        if_press_mesh=False if 'F' in header_list[13] else True,
        float_fmt='f' if int(header_list[1]) == 4 else 'd',
        int_size=4,
        int_fmt='i'
    )

    print(header_list)
    print(hinfo)

    endian = np.fromfile(f, dtype=np.float32, count=1)[0]

    # TODO: Make dtype a variable
    glob_el_nums = np.fromfile(f, dtype=np.int32, count=hinfo.nelt)
    print(glob_el_nums)
