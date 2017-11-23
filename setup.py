from setuptools import setup, find_packages
from os.path import join, dirname
from qtar import __version__

COMMON_SETUP_PARAMS = dict(
    name='QTAR_Stego',
    version=__version__,
    description=open(join(dirname(__file__), 'README.txt')).read()
)

setup(
    **COMMON_SETUP_PARAMS,
    packages=find_packages(),
    url='',
    license='Apache-2.0',
    test_suite='qtar.tests',
    author='Andrey',
    author_email='andrayosipov@gmail.com',
    entry_points={
        'console_scripts': [
            'qtar = qtar.cli:main',
            'qtar-de = qtar.optimization.de:main',
            'qtar-exp = qtar.experiments.cli:main'
        ]
    },
    install_requires=[
        'numpy>=1.13, <2.0',
        'scipy>=1.0, <2.0',
        'pillow>=4.3, <5.0',
        'scikit-image>=0.13, <1.0',
        'matplotlib>=2.1, <3.0',
        'pandas>=0.21, <1.0',
        'openpyxl>=2.4, <3.0'
    ]
)