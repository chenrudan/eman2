#!/usr/bin/env python

import os
import site

spdir = site.getsitepackages()[0] # current environment's site packages directory
egginfo = max([i for i in os.listdir(spdir) if "eman2" in i if "egg-info" in i]) # get most recent version if multiple are present
e2real = "{}/{}/scripts/e2_real.py".format(spdir,egginfo)

os.execlp("ipython","ipython","-i",e2real)

