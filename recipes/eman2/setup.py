from setuptools import setup
import glob

#scripts = [name for name in glob.glob('lib/bin/*.py')] # separated EMAN and sparx programs into respective libs
scripts = [name for name in glob.glob('bin/*.py')]

e2_pkgdata = ['*.so','*.dylib','pmconfig/*','pyemtbx/*','include/*.h','include/gorgon/*.h','include/plugins/*.h','include/sparx/*.h','examples/*.py','fonts/*.txt','fonts/*.ttf','images/*.png','images/*.ico','images/macimages/*.png','doc/*','test/rt/*.py']

sx_pkgdata = ['*.so','*.dylib','pyemtbx/*','include/*.h','include/plugins/*.h','include/sparx/*.h','examples/*.py','fonts/*.txt','fonts/*.ttf','images/*.png','images/*.ico','images/macimages/*.png','doc/*','test/rt/*.py']

setup(
    name="eman2",
    version="3.0",
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
