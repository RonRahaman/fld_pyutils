from fld_data_memmap import FldDataMemmap
from fld_data import FldData

#d1 = FldDataMemmap.fromfile('demos/data/test0.f00001')
d1 = FldData.fromfile('testA/rod_short0.f00001')
d1.plot()
