

set -ex



python -V
python3 -V
2to3 -h
pydoc -h
python3-config --help
python -m venv test-venv
python -c "import sysconfig; print(sysconfig.get_config_var('CC'))"
for f in ${CONDA_PREFIX}/lib/python*/_sysconfig*.py; do echo "Checking $f:"; if [[ `rg @ $f` ]]; then echo "FAILED ON $f"; cat $f; exit 1; fi; done
test ! -f ${PREFIX}/lib/libpython${PKG_VERSION%.*}.a
test ! -f ${PREFIX}/lib/libpython${PKG_VERSION%.*}.nolto.a
pushd tests
pushd distutils
python setup.py install -v -v
python -c "import foobar"
popd
pushd distutils.cext
python setup.py install -v -v
python -c "import greet; greet.greet('Python user')" | rg "Hello Python"
popd
pushd prefix-replacement
bash build-and-test.sh
popd
pushd cmake
cmake -GNinja -DPY_VER=3.8.13
popd
popd
test ! -f default.profraw
exit 0
