from setuptools import setup, find_packages
import glob

scripts = glob.glob('lib/bin/*.py')
#images = glob.glob('lib/images/*')
#macimages = glob.glob('lib/images/macimages/*')
#pmconfig = glob.glob('lib/libEM/pmconfig/*')
#fonts = glob.glob('lib/fonts/*')
#examples = glob.glob('lib/examples/*')
#docs = glob.glob('lib/doc/*')

setup(
    name="eman2",
    version="3.0.0",
    description="A scientific image processing software suite with a focus on CryoEM and CryoET",
    author="Steve Ludtke",
    author_email="sludtke@bcm.edu",
    license="GNU General Public License, Version 2",
    url="http://blake.bcm.edu/emanwiki/EMAN2",
    package_dir={'EMAN2':'lib'},
    packages=find_packages(), #{'EMAN2':'EMAN2','EMAN2.pyemtbx':'EMAN2.pyemtbx'},
    package_data={'EMAN2':['lib/*.so','lib/*.dylib'],
    	    'EMAN2/pmconfig':['lib/libEM/pmconfig/*'],
    	    'EMAN2/images':['lib/images/*'],
    	    'EMAN2/images/macimages':['lib/images/macimages/*'],
    	    'EMAN2/fonts':['lib/fonts/*'],
    	    'EMAN2/examples':['lib/examples/*'],
    	    'EMAN2/doc':['lib/doc/*']},
    include_package_data = True,
    scripts=scripts,
    zip_safe = False,
)
