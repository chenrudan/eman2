#!/usr/bin/env python

import os
#import sys
import site

e2real = "{}/eman2-3.0.0-py2.7.egg-info/scripts/e2_real.py".format(site.getsitepackages()[0])
#e2real="{}/bin/e2_real.py".format(sys.exec_prefix)
#e2real="{}/bin/e2_real.py".format(os.getenv("EMAN2DIR"))
os.execlp("ipython","ipython","-i",e2real)

