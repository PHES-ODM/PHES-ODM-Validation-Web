import platform
from pathlib import Path

from cx_Freeze import setup, Executable
from odm_validation import validation

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {
    'include_files': ['src'],
    'include_path': ['src'],
    'includes': ['odm_validation'],
    'packages': ['sqlalchemy'],
}

# fix: include odm-validation assets for windows installers
if platform.system() == 'Windows':
    pkgdir = Path(validation.__file__).parent
    assetdir = pkgdir / 'assets'
    build_options['include_files'].append(
        (assetdir, 'lib/odm_validation/assets'))

base = 'console'

executables = [
    Executable('src/entry.py', target_name='odm-webtool', base=base)
]

setup(name='odm-webtool',
      version = '1.0',
      description = '',
      options = {'build_exe': build_options},
      executables = executables)
