#!/bin/bash

#http://conda-test.pydata.org/docs/build.html

cmake $SRC_DIR
make
make install

