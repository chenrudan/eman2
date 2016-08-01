#!/bin/bash

build_dir="${SRC_DIR}/../build_dir"

mkdir -p $build_dir
cd $build_dir

cmake $SRC_DIR

make -j
make install

$PYTHON "${RECIPE_DIR}/setup.py" install
