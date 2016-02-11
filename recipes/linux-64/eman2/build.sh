#!/bin/bash

cmake NUMPY_INCLUDE_PATH=$SP_DIR/numpy/core/include PYTHON_INCLUDE_PATH=$PREFIX/include/python2.7 EMAN_INSTALL_PREFIX=$PREFIX CMAKE_SKIP_RPATH=ON $SRC_DIR
make -j"${CPU_COUNT}"
make install

