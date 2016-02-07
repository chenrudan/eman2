#!/bin/bash

cmake NUMPY_INCLUDE_PATH=$SP_DIR/numpy/core/include PYTHON_INCLUDE_PATH=$PREFIX/include/python2.7 $SRC_DIR

echo "$(cmake -LA)"

make -j4
make install

