from setuptools import setup #, find_packages
import glob

scripts = [name for name in glob.glob('lib/bin/*.py')]

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
    package_data={'EMAN2':['*.so','*.dylib','examples/*.py','fonts/*.txt','fonts/*.tff','images/*.png','images/*.ico','pmconfig/*.json','pyemtbx/*.py','doc/*'],'':['include/*.h','include/gorgon/*.h','include/plugins/*.h','test/rt/*.py']},
    include_package_data = True,
    scripts=scripts,
    zip_safe = False,
)
