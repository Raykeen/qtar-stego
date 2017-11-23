from setup import COMMON_SETUP_PARAMS
from cx_Freeze import setup, Executable

base = None

setup(
    **COMMON_SETUP_PARAMS,
    options={
        'build_exe': {
            'packages': ["qtar.cli"],
            'includes': ['numpy.core._methods', 'numpy.lib.format', 'scipy.ndimage._ni_support']
        }
    },
    executables=[Executable("qtar\\cli\\cli.py", icon='icon.ico', base=base)]
)
