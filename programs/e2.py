#!/usr/bin/env python

import os

e2real="{}/bin/e2_real.py".format(sys.exec_prefix) #os.getenv("EMAN2DIR")+"/bin/e2_real.py"
os.execlp("ipython","ipython","-i",e2real)

