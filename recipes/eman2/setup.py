from setuptools import setup, find_packages
import glob

scripts = [name for name in glob.glob('lib/bin/*.py')]

setup(
    name="eman2",
    version="3.0.0",
    description="A scientific image processing software suite with a focus on CryoEM and CryoET",
    author="Steve Ludtke",
    author_email="sludtke@bcm.edu",
    license="GNU General Public License, Version 2"
    url="http://blake.bcm.edu/emanwiki/EMAN2",

    package_dir={'EMAN2':'libeman/EMAN2'},
    # packages=find_packages('EMAN2'),
    packages={'EMAN2':'EMAN2',
              #'EMAN2.qtgui':'EMAN2.qtgui',
              'EMAN2.pyemtbx':'EMAN2.pyemtbx',
              'EMAN2.pmconfig':'EMAN2.pmconfig',
              },
    include_package_data = True,
    package_data={'EMAN2':['*.so'],
    	    'images':['*.png','*.jpg','*.ico'],
    	    'fonts':['*.txt','*.ttf'],
    	    'examples':['*.py'],
    	    'doc':['*.html','*.txt'],
    	    },
    scripts=scripts,
    # entry_points={
    #     'console_scripts': [
    #         'gorgon=run.gorgon:main',
    #     ],
    # },
    zip_safe = False,
)
