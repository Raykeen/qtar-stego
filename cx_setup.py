from setup import COMMON_SETUP_PARAMS
from cx_Freeze import setup, Executable

base = None

setup(
    **COMMON_SETUP_PARAMS,
    options={
        'build_exe': {
            'packages': ['qtar.cli', 'qtar.experiments.cli', 'qtar.optimization.de'],
            'optimize': 1,
            'include_files': ['images', 'experiments'],
            'includes': ['numpy.core._methods', 'numpy.lib.format', 'scipy.ndimage._ni_support'],
            'silent': True
        }
    },
    executables=[
        Executable("qtar\\cli\\cli.py", targetName='qtar.exe', icon='icon.ico', base=base),
        Executable("qtar\\experiments\\cli.py", targetName='qtar-exp.exe', base=base),
        Executable("qtar\\optimization\\de.py", targetName='qtar-de.exe', base=base)
    ]
)
