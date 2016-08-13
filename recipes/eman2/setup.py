from setuptools import setup
import glob
import os

libdir='lib'
e2_scripts = [name for name in glob.glob(os.path.join(libdir,'bin','e2.py'))]

e2_pkgdata = ['libpyAligner2.so']

setup(
	name="eman2",
	version="3.0.0",

    package_dir={'EMAN2':os.path.join(libdir,'EMAN2'),},
    packages=['EMAN2',],
    package_data={'EMAN2':e2_pkgdata,},
    include_package_data = True,
    scripts = e2_scripts,
    
    zip_safe = False,

	description="A scientific image processing software suite with a focus on CryoEM and CryoET",
	author="Steve Ludtke",
	author_email="sludtke@bcm.edu",
	license="GNU General Public License, Version 2",
	url="http://blake.bcm.edu/emanwiki/EMAN2",
)
