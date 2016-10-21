# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -----------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

#x = np.linspace(0,10,51)
#y = np.linspace(0,8,41)
#(X,Y) = np.meshgrid(x,y)
#a = np.exp(-((X-2.5)**2 + (Y-4)**2)/4) - np.exp(-((X-7.5)**2 + (Y-4)**2)/4)
#c = plt.contour(x,y,a)
#l = plt.clabel(c)
#lx = plt.xlabel("x")
#ly = plt.ylabel("y")
#plt.savefig('/home/julian/Dropbox/QPE/resultados/resultados_zr/test_contour.png', format = 'png',\
#           dpi = 400)


npr = np.random
npts = 3000.                            # the total number of data points.
x = npr.normal(size=npts)    
y = np.linspace(0,100, npts) + npr.normal(size=npts)            # ... do the same for y.
H, edgex, edgey = np.histogram2d(x, y, bins = 30)
mean_edgex = edgex[0:-1] + (edgex[1:] - edgex[0:-1])/2
mean_edgey = edgey[0:-1] + (edgey[1:] - edgey[0:-1])/2
X,Y = np.meshgrid(mean_edgex, mean_edgey)

plt.close()
plt.cla()
plt.clf()
plt.scatter(x, y,marker = '.', s = 6, color = 'k', alpha = 0.4)
plt.contourf(X, Y, np.transpose(H))
plt.savefig('/home/julian/Dropbox/QPE/resultados/resultados_zr/test_contour.pdf', format = 'pdf',\
           dpi = 400)
