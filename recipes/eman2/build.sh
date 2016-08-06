#!/bin/bash

echo "SOURCE DIR: ${SRC_DIR}"

build_dir="${SRC_DIR}/../build_dir"

mkdir -p $build_dir
cd $build_dir

cmake $SRC_DIR

make -j
make install

#echo "RECIPE DIR: ${RECIPE_DIR}" # ${HOME}/src/eman2-conda/recipes/eman2
$PYTHON "${RECIPE_DIR}/setup.py" install # relative to build environment
#$PYTHON "${SRC_DIR}/recipes/setup.py" install # relative to build environment

