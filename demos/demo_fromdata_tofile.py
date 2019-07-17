from fld_data import FldData
import numpy as np

ndims = 3
nx1 = 3  #don't change this for now
ny1 = nx1
nz1 = nx1
nelgt = 10  #change this all you want
nelt = nelgt

float_type = np.dtype(np.float32)
int_type = np.dtype(np.int32)

glel = np.arange(1, nelt + 1)

pt =[[0.0, 0.0, 0.0],
     [0.5, 0.0, 0.0],
     [1.0, 0.0, 0.0],
     [0.0, 0.5, 0.0],
     [0.5, 0.5, 0.0],
     [1.0, 0.5, 0.0],
     [0.0, 1.0, 0.0],
     [0.5, 1.0, 0.0],
     [1.0, 1.0, 0.0],
     [0.0, 0.0, 0.5],
     [0.5, 0.0, 0.5],
     [1.0, 0.0, 0.5],
     [0.0, 0.5, 0.5],
     [0.5, 0.5, 0.5],
     [1.0, 0.5, 0.5],
     [0.0, 1.0, 0.5],
     [0.5, 1.0, 0.5],
     [1.0, 1.0, 0.5],
     [0.0, 0.0, 1.0],
     [0.5, 0.0, 1.0],
     [1.0, 0.0, 1.0],
     [0.0, 0.5, 1.0],
     [0.5, 0.5, 1.0],
     [1.0, 0.5, 1.0],
     [0.0, 1.0, 1.0],
     [0.5, 1.0, 1.0],
     [1.0, 1.0, 1.0]]

nxyz=nx1*ny1*nz1
coords=np.empty((nelt,ndims,nxyz),dtype=float_type)
u=np.empty((nelt,ndims,nxyz),dtype=float_type)
for j in range(nelt):
  for i in range(nxyz):
    coords[j][0][i]=pt[i][0]
    coords[j][1][i]=pt[i][1]
    coords[j][2][i]=pt[i][2]+float(j)  #offset in the z-direction by the element number
    u[j][0][i]=float(j)+1.0
    u[j][1][i]=(float(j)+1.0)*2.0
    u[j][2][i]=(float(j)+1.0)*3.0

#p = np.full(nelt * nx1 ** 3, fill_value=8)

i=1.0
p=np.arange(i,i+nelt*nxyz,dtype=float)

i=i+nelt*nxyz
t = np.arange(i,i+nelt*nxyz,dtype=float)

data = FldData.fromvalues(nx1=nx1, ny1=ny1, nz1=nz1, nelgt=nelgt, nelt=nelt,
                         glel=glel, coords=coords, p=p, u=u, t=t)

data.tofile('fdtf0.f00001')
print(data)

