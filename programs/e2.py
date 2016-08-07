#!/usr/bin/env python

import os
import sys

e2real="{}/bin/e2_real.py".format(sys.exec_prefix)
#e2real="{}/bin/e2_real.py".format(os.getenv("EMAN2DIR"))
os.execlp("ipython","ipython","-i",e2real)

