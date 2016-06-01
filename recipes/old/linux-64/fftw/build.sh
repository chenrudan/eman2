#!/usr/bin/env bash

./configure --prefix=$PREFIX --enable-shared --enable-float 
make -j"$CPU_COUNT"
make install

