from fld_data_memmap import FldDataMemmap

d1 = FldDataMemmap.fromfile('testA/rod_short0.f00001')
d1.tofile('testB/rod_short0.f00001')
