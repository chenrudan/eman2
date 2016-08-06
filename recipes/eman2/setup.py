from setuptools import setup #, find_packages
import glob
import os

libdir='install_dir'
scripts = [name for name in glob.glob(os.path.join(libdir,'bin', '*.py'))]

setup(
	name="eman2",
	version="3.0.0",

    package_dir={'EMAN2':'libeman/EMAN2','sparx':'libeman/sparx'},
    packages=['EMAN2','sparx'],
    package_data={'EMAN2':['*.so','*.dylib','pmconfig/*','pyemtbx/*'],
    	    '':['include/*.h','include/gorgon/*.h','include/plugins/*.h',
    	    	    'examples/*.py','fonts/*.txt','fonts/*.ttf',
    	    	    'images/*.png','images/*.ico','doc/*','test/rt/*.py']},
    include_package_data = True,
    scripts=scripts,
    
    zip_safe = False,

	description="A scientific image processing software suite with a focus on CryoEM and CryoET",
	author="Steve Ludtke",
	author_email="sludtke@bcm.edu",
	license="GNU General Public License, Version 2",
	url="http://blake.bcm.edu/emanwiki/EMAN2",
)
