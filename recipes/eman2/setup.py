from setuptools import setup, find_packages
import glob

scripts = [name for name in glob.glob('lib/bin/*.py')]

setup(
    name="eman2",
    version="2.2",

    package_dir={'':'lib',
                 'bin':'lib/bin',
                 'lib':'lib/EMAN2'},
    packages=find_packages(),
    package_data={'':['*.so']},

    scripts=scripts,
    # entry_points={
    #     'console_scripts': [
    #         'gorgon=run.gorgon:main',
    #     ],
    # },
    
    zip_safe = False,
)
