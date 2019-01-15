import struct
import numpy as np

with open('data/test0.f00001', 'rb') as f:
    header = f.read(132).decode(encoding='ascii')
    header_list = header.split()

    hdict = dict(
        wdsize=int(header_list[1]),
        nx=int(header_list[2]),
        ny=int(header_list[3]),
        nz=int(header_list[4]),
        nelo=int(header_list[5]),
        nelgt=int(header_list[6]),
        time=float(header_list[7]),
        iostep=int(header_list[8]),
        fid0=int(header_list[9]),
        nfileoo=int(header_list[10]),
        rdcode=header_list[11])

    print(hdict)

    float_fmt = 'f' if hdict['wdsize'] == 4 else 'd'

    endian = struct.unpack('f', f.read(4))

    nxyz = hdict['nx'] * hdict['ny'] * hdict['nz']

    # TODO: garbage
    vals = np.array(struct.unpack(float_fmt * nxyz, f.read(nxyz * hdict['wdsize'])), dtype=float_fmt)
    print(vals)
