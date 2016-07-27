from setuptools import setup, find_packages
import glob

scripts = [name for name in glob.glob('lib/bin/*.py')]

setup(
    name="eman2",
    version="2.2",

    package_dir={'EMAN2':'libCMAKE/EMAN2'},
    # packages=find_packages('EMAN2'),
    packages={'EMAN2':'EMAN2',
              'EMAN2.qtgui':'EMAN2.qtgui',
              'EMAN2.pyemtbx':'EMAN2.pyemtbx',
              },
    package_data={'EMAN2':['*.so']},

    scripts=scripts,
    # entry_points={
    #     'console_scripts': [
    #         'gorgon=run.gorgon:main',
    #     ],
    # },

    zip_safe = False,
)
