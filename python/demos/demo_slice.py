from fld_data import FldData
import numpy as np

d1 = FldData.fromfile('../testA/rod_short0.f00001')
d2 = d1.slice(maxes=[0, 0.5, 6])
d2.tofile('../testB/rod_short0.f00001')
