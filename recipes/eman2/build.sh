#!/bin/bash

build_dir="${SRC_DIR}/../build_dir"

mkdir -p $build_dir
cd $build_dir

cmake $SRC_DIR

make -j"$(bc -l <<< ${CPU_COUNT}-2)"
make install

cp "${RECIPE_DIR}/setup.py" .
$PYTHON setup.py install
