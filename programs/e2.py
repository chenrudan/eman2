#!/usr/bin/env python

#import os
from EMAN2 import * # we define EMAN2DIR in __init__.py and import os

e2real=os.getenv("EMAN2DIR")+"/bin/e2_real.py"
os.execlp("ipython","ipython","-i",e2real)

