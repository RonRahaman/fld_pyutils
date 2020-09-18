from fld_data_memmap import FldDataMemmap

d1 = FldDataMemmap.fromfile('testC/test0.f00001')
#d1 = FldDataMemmap.fromfile('testA/rod_short0.f00001')
d1.plot()
