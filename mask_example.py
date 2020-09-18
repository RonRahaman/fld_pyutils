import numpy as np
#import matplotlib.pyplot as plt

x = np.linspace(-1, 1, 8)
y = np.linspace(-1, 1, 8)
xx, yy = np.meshgrid(x, y)
#p = np.sin(xx**2 + yy**2) / (xx**2 + yy**2)

coords = np.vstack([xx.reshape(1,-1), yy.reshape(1, -1)])
p = np.sin(coords[0]**2 + coords[1]**2) / (coords[0]**2 + coords[1]**2)

print(coords)
mask = coords[coords[0] < 0, :]
print(mask)

#plt.scatter(coords[0], coords[1], c=p)
#plt.show()

