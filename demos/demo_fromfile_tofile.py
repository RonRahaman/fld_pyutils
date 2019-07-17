from fld_data import FldData

d1 = FldData.fromfile('data/test0.f00001')
d1.tofile('fftf0.f00001')
print(d1)

print('*' * 60)


d2 = FldData.fromfile('fftf0.f00001')
print(d2)
