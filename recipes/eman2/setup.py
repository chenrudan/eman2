#!/usr/bin/env python

from setuptools import setup
import glob
import time

### replacing the timestamp in e2version.py, Muyuan 2015
now = time.ctime()

with open("lib/bin/e2version.py","r") as e2ver_in:
    lines = e2ver_in.readlines()

with open("lib/bin/e2version.py","w") as e2ver_out:
    for l in lines:
        e2ver_out.write(l.replace("BUILD_DATE",now))

# grabbing all executables
scripts = [name for name in glob.glob('lib/bin/*.py')]

# grabbing all package data
e2_pkgdata = ['*.so','*.dylib','pmconfig/*','pyemtbx/*','include/*.h','include/gorgon/*.h','include/plugins/*.h','include/sparx/*.h','examples/*.py','fonts/*.txt','fonts/*.ttf','images/*.png','images/*.ico','images/macimages/*.png','doc/*','test/rt/*.py']

sx_pkgdata = ['*.so','*.dylib','pyemtbx/*','include/*.h','include/plugins/*.h','include/sparx/*.h','examples/*.py','fonts/*.txt','fonts/*.ttf','images/*.png','images/*.ico','images/macimages/*.png','doc/*','test/rt/*.py']

# packaging eman2 for distribution
setup(
    name="eman2",
    version="3.0.0",
    description="A scientific image processing software suite with a focus on CryoEM and CryoET",
    author="Steve Ludtke",
    author_email="sludtke@bcm.edu",
    license="GNU General Public License, Version 2",
    url="http://blake.bcm.edu/emanwiki/EMAN2",
    package_dir={'EMAN2':'libeman/EMAN2','sparx':'libeman/sparx'},
    packages=['EMAN2','sparx'],
    package_data={'EMAN2':e2_pkgdata,'sparx':sx_pkgdata},
    include_package_data = True,
    scripts=scripts,
    zip_safe = False,
)

