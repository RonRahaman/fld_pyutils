from fld_data import FldData
import numpy as np

ndims = 3
nx1 = 7
ny1 = nx1
nz1 = nx1
nelgt = 512
nelt = nelgt
float_type = np.dtype(np.float32)
int_type = np.dtype(np.int32)

glel = np.arange(1, nelt + 1)

coords = np.vstack((np.full(nelt * nx1 ** 3, fill_value=2),
                    np.full(nelt * nx1 ** 3, fill_value=3),
                    np.full(nelt * nx1 ** 3, fill_value=4))).transpose()

u = np.vstack((np.full(nelt * nx1 ** 3, fill_value=5),
               np.full(nelt * nx1 ** 3, fill_value=6),
               np.full(nelt * nx1 ** 3, fill_value=7)))

p = np.full(nelt * nx1 ** 3, fill_value=8)

t = np.full(nelt * nx1 ** 3, fill_value=9)

data = FldData.fromvalues(nx1=nx1, ny1=ny1, nz1=nz1, nelgt=nelgt, nelt=nelt,
                         glel=glel, coords=coords, u=u, p=p, t=t)

data.tofile('scratch.fld')

data2 = FldData.fromfile('scratch.fld')
print(data2)
