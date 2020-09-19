from fld_data_memmap import FldDataMemmap
import numpy as np

d1 = FldDataMemmap.fromfile('data/test0.f00001', mode="c")
print(d1)

print('*' * 60)

d1.u = np.full_like(d1.u, 0)
d1.tofile('fftf0.f00001')

d2 = FldDataMemmap.fromfile('fftf0.f00001')
print(d2)

d3 = FldDataMemmap.fromfile('data/test0.f00001', mode="r")
print(d3)
