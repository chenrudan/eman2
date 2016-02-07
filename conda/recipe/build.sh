#!/bin/bash

#http://conda-test.pydata.org/docs/build.html

# CMAKE VARS
#cmake BOOST_INCLUDE_PATH=$PREFIX/include BOOST_LIBRARY=$PREFIX/lib/libboost_python.dylib FREETYPE_INCLUDE_PATH=$PREFIX/include/freetype2 NUMPY_INCLUDE_PATH=$SP_DIR/numpy/core/include PYTHON_INCLUDE_PATH=$PREFIX/include/python2.7 EMAN_INSTALL_PREFIX=$PREFIX $SRC_DIR

cmake NUMPY_INCLUDE_PATH=$SP_DIR/numpy/core/include PYTHON_INCLUDE_PATH=$PREFIX/include/python2.7 EMAN_INSTALL_PREFIX=$PREFIX $SRC_DIR

echo "$(cmake -LAH | grep FREETYPE)"

make -j8
make install

