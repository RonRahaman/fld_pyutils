from fld_data import FldData
import numpy as np

ndims = 3
nx1 = 2
ny1 = nx1
nz1 = nx1
float_type = np.dtype(np.float32)
int_type = np.dtype(np.int32)

vcrds=np.loadtxt('data/vcoord.txt')
x=vcrds[:,0]
y=vcrds[:,1]
z=vcrds[:,2]

vdat=np.loadtxt('data/vdata.txt',skiprows=1)
vid=vdat[:,0].astype(int)
power=vdat[:,1]
flux=vdat[:,2]

nvrt = len(vcrds)
nelt = int(len(vdat)/8)
print(nvrt," vertices in ",nelt," elements")

glel = np.arange(1,nelt+1)
po=[]
to=[]

nxyz=nx1*ny1*nz1
coords=np.empty((nelt,ndims,nxyz))
for i in range(nelt):
  for j in range(nxyz):
    k = i * nxyz + j
    l = vid[k]
    coords[i][0][j] = x[l]
    coords[i][1][j] = y[l]
    coords[i][2][j] = z[l]
    po.append(power[k])
    to.append(flux[k])

p = np.array(po).reshape((nelt, nxyz))
t = np.array(to).reshape((nelt, nxyz))

data = FldData.fromvalues(nx1=nx1, ny1=ny1, nz1=nz1, nelgt=nelt, nelt=nelt, glel=glel,
                          coords=coords, p=p, t=t)

data.tofile('proteus0.f00001')
