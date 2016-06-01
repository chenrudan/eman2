#!/bin/bash

cmake -DPYTHON_INCLUDE_PATH:PATH=$PREFIX/include/python2.7 -DNUMPY_INCLUDE_PATH:PATH=$PREFIX/lib/python2.7/site-packages/numpy/core/include -DEMAN_INSTALL_PREFIX:PATH=$PREFIX $SRC_DIR
make -j"${CPU_COUNT}"
make install

