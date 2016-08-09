from setuptools import setup, find_packages
import glob

scripts = [name for name in glob.glob('lib/bin/*.py')]

setup(
	name="eman2",
	version="3.0.0",

    package_dir={'':'lib',
                 'bin':'lib/bin',
                 'lib':'lib/EMAN2'},
    packages=find_packages(),
    package_data={'':['*.so']},

    scripts=scripts,
    
    zip_safe = False,

	description="A scientific image processing software suite with a focus on CryoEM and CryoET",
	author="Steve Ludtke",
	author_email="sludtke@bcm.edu",
	license="GNU General Public License, Version 2",
	url="http://blake.bcm.edu/emanwiki/EMAN2",
)
