#!/usr/bin/env python

from EMAN2 import *
import numpy as np

a = test_image()
a.write_image("twod_image.hdf")

b = test_image(9)
for i in range(6):
    b.write_image("twod_stack.hdf",i)

c = test_image_3d(1)
c.write_image("threed_volume.hdf")

for i in range(6):
    d = test_image_3d(i)
    d.write_image("threed_stack.hdf",i)

e = np.random.normal(0,1,(100,2))
np.savetxt("twod_data.txt",e,delimiter="\t")

