#!/bin/bash

./configure --prefix=$PREFIX --with-zlib=yes --with-bzip2=no --with-png=yes --without-harfbuzz --enable-shared
make
make install

