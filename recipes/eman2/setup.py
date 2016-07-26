from setuptools import setup, find_packages

setup(
    name="eman2",
    version="3",

    package_dir={'':'lib',
                 'bin':'lib/bin',
                 'lib':'lib/EMAN2'},
    packages=find_packages(),
    package_data={'':['*.so']},

    scripts=['lib/bin/*.py'],
    
    zip_safe = False,
)
