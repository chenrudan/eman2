from setuptools import setup, find_packages
import glob

scripts = [name for name in glob.glob('lib/bin/*.py')]

setup(
    name="EMAN2",
    version="3.0.0",
    description="A scientific image processing software suite with a focus on CryoEM and CryoET",
    author="Steve Ludtke",
    author_email="sludtke@bcm.edu",
    license="GNU General Public License, Version 2",
    url="http://blake.bcm.edu/emanwiki/EMAN2",
    package_dir={'EMAN2':'libeman/EMAN2','sparx':'libeman/sparx'},
    packages=find_packages(), #{'EMAN2':'EMAN2','EMAN2.pyemtbx':'EMAN2.pyemtbx','sparx':'sparx'},
    package_data={'EMAN2':['*.so','*.dylib'],
    	    'EMAN2/pmconfig':['libeman/pmconfig/*.json'],
    	    'EMAN2/examples':['libeman/examples/*'],
    	    'EMAN2/images':['libeman/images/*'],
    	    'EMAN2/images/macimages':['libeman/images/macimages/*'],
    	    'EMAN2/fonts':['libeman/fonts/*'],
    	    'EMAN2/doc':['libeman/doc/*']},
    include_package_data = True,
    scripts=scripts,
    zip_safe = False,
)
