installdir=$(dirname "$0")
rootdir=$installdir/..

cd $rootdir

# noconfirm:
# - overwrites previous build without asking

# paths src:
# - specifies import path of app's modules

# add-data src:
# - solves an exception during validation
# - includes app source for exception stacktrace
# - includes pages dir for dash's dynamic imports
# - includes assets dir for stylesheet, etc.

# collect-all odm_validation:
# - includes its assets

# pack
pyinstaller \
    --noconfirm \
    --paths ./src \
    --add-data src:. \
    --collect-all odm_validation \
    ./src/app.py

# run
./dist/app/app
