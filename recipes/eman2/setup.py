from setuptools import setup, find_packages
import glob
import os

libdir='install_dir'
scripts = [name for name in glob.glob(os.path.join(libdir,'bin', '*.py'))]

setup(
	name="eman2",
	version="3.0.0",

    package_dir={'EMAN2':'libeman/EMAN2',
    	    'sparx':'libeman/sparx'
    	    },
    packages={'EMAN2':'EMAN2',
    	    'EMAN2.pyemtbx':'EMAN2.pyemtbx',
    	    'sparx':'sparx',
    	    },
    package_data={'EMAN2':['*.so','*.dylib'],
    	    'EMAN2/pmconfig':['libEM/pmconfig/*.json'],
    	    'EMAN2/images':['lib/images/*.png',
    	    	    'images/*.ico',
    	    	    'images/macimages/*.png',
    	    	    'images/macimages/*.ico',
    	    	    ],
    	    'EMAN2/fonts':['fonts/*.txt',
    	    	    'fonts/*.ttf'],
    	    'EMAN2/examples':['examples/*.py',
    	    	    'examples/*.jpg',
    	    	    'examples/00README'],
    	    'EMAN2/doc':['doc/*.html',
    	    	    'doc/*.txt',
    	    	    'doc/build/*',
    	    	    'doc/doxygen/*',
    	    	    'doc/latex/*',
    	    	    'doc/modular_class_html/*.py'],
    	    },
    include_package_data = True,
    scripts=scripts,
    
    zip_safe = False,

	description="A scientific image processing software suite with a focus on CryoEM and CryoET",
	author="Steve Ludtke",
	author_email="sludtke@bcm.edu",
	license="GNU General Public License, Version 2",
	url="http://blake.bcm.edu/emanwiki/EMAN2",
)
