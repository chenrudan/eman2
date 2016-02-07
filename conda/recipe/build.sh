#!/bin/bash

echo $PREFIX
echo $SRC_DIR

cmake
make
make install

