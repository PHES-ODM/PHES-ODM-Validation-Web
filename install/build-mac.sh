set -ex

name=odm-webtool
installdir=$(dirname $0)

# build
python3 $installdir/setup.py bdist_mac

# zip
builddir=$installdir/../build
pushd $builddir
    distdir_old=$(ls -t1 | grep exe.macosx | head -n 1)
    distdir_new=$name-$distdir_old
    mv $distdir_old $distdir_new
    archive=$name-mac.zip
    zip -r $archive $distdir_new
popd
