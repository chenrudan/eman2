from setuptools import setup, find_packages
import glob
import os

libdir='install_dir'
scripts = [name for name in glob.glob(os.path.join(libdir,'bin', '*.py'))]

setup(
	name="eman2",
	version="3.0.0",

    package_dir={'EMAN2':os.path.join(libdir, 'EMAN2')},
    # packages=find_packages('EMAN2'),
    packages={'EMAN2':'EMAN2',
              'EMAN2.pyemtbx':'EMAN2.pyemtbx',
              },
    package_data={'EMAN2':['*.so']},

    scripts=scripts,
    
    zip_safe = False,

	description="A scientific image processing software suite with a focus on CryoEM and CryoET",
	author="Steve Ludtke",
	author_email="sludtke@bcm.edu",
	license="GNU General Public License, Version 2",
	url="http://blake.bcm.edu/emanwiki/EMAN2",
)
