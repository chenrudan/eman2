#!/bin/bash

cmake NUMPY_INCLUDE_PATH=$SP_DIR/numpy/core/include PYTHON_INCLUDE_PATH=$PREFIX/include/python2.7 EMAN_INSTALL_PREFIX=$PREFIX/EMAN2 $SRC_DIR
make -j4
make install

