#!/bin/bash

# SOURCE DIR: ${HOME}/anaconda/conda-bld/work
build_dir="${SRC_DIR}/../build_dir"

mkdir -p $build_dir
cd $build_dir

cmake $SRC_DIR

make -j
make install

#RECIPE DIR: ${HOME}/src/eman2-conda/recipes/eman2
$PYTHON "${RECIPE_DIR}/setup.py" install # relative to build environment

