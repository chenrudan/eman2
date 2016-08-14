#!/bin/bash

./configure --prefix=$PREFIX --enable-linux-lfs --with-zlib=$PREFIX --with-ssl --enable-cxx --enable-shared
make
make install

rm -rf $PREFIX/share/hdf5_examples

