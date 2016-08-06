#!/bin/bash

# SOURCE DIR: conda-bld/work
build_dir="${SRC_DIR}/../build_dir"

mkdir -p $build_dir
cd $build_dir

cmake $SRC_DIR

make -j
make install

#RECIPE DIR: eman2(gitrepo)/recipes/eman2
$PYTHON "${RECIPE_DIR}/setup.py" install

