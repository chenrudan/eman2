#!/bin/bash

case "$(uname -s)" in
	Darwin*)  OS="mac" ;; 
	Linux*)   OS="linux" ;;
	*)        OS="other" ;;
esac

if [[ $OS == "linux" ]]; then
	cmake NUMPY_INCLUDE_PATH=$SP_DIR/numpy/core/include PYTHON_INCLUDE_PATH=$PREFIX/include/python2.7 EMAN_INSTALL_PREFIX=$PREFIX $SRC_DIR
elif [[ $OS == "mac" ]]; then
	cmake NUMPY_INCLUDE_PATH=$SP_DIR/numpy/core/include PYTHON_INCLUDE_PATH=$PREFIX/include/python2.7 EMAN_INSTALL_PREFIX=$PREFIX CMAKE_SKIP_RPATH=ON $SRC_DIR
fi

make -j"${CPU_COUNT}"
make install

