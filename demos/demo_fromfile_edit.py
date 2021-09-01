from fld_data import FldData
import numpy as np

d = FldData.fromfile('data/test0.f00001')

d.p = np.full((d.nelt, d.nx1 * d.ny1 * d.nz1), fill_value=99)

print(d)

