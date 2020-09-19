from fld_data_memmap import FldDataMemmap

d1 = FldDataMemmap.fromfile('data/test0.f00001', mode="r")
print(d1)

print('*' * 60)

d1.tofile('fftf0.f00001')
d2 = FldDataMemmap.fromfile('fftf0.f00001')
print(d2)
