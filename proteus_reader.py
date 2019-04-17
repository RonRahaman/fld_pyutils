import numpy as np

vcrds=np.loadtxt('data/vcoord.txt')
x=vcrds[:,0]
y=vcrds[:,1]
z=vcrds[:,2]

vdat=np.loadtxt('data/vdata.txt',skiprows=1)
vid=vdat[:,0].astype(int)
power=vdat[:,1]
flux=vdat[:,2]

nvrt = len(vcrds)
nelv = len(vdat)/8
print(nvrt," vertices in ",nelv," elements")

xo=[]
yo=[]
zo=[]
for i in vid:
    xo.append(x[vid[i]])
    yo.append(y[vid[i]])
    zo.append(z[vid[i]])

