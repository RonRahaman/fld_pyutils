from fld_data import FldData

d1 = FldData.fromfile('data/test0.f00001')
d1.tofile('data/scratch.fld')

d2 = FldData.fromfile('data/scratch.fld')
print(d2)