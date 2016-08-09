#!/bin/bash

case "$(uname -s)" in
	Darwin*)  OS="mac" ;; 
	Linux*)   OS="linux" ;;
	*)        OS="other" ;;
esac

PY_INC=${PREFIX}/include/python2.7
NPY_INC=${PREFIX}/lib/python2.7/site-packages/numpy/core/include

#echo "PYTHON_INCLUDE_PATH: ${PY_INC}"
#echo "NUMPY_INCLUDE_PATH: ${NPY_INC}"
#echo "OS: ${OS}"
#echo "SRC_DIR: ${SRC_DIR}"
#echo "SP_DIR: ${SP_DIR}"
#echo "PREFIX: ${PREFIX}"

if [[ $OS == "linux" ]]; then
	cmake -DNUMPY_INCLUDE_PATH=${NPY_INC} -DPYTHON_INCLUDE_PATH=${PY_INC} -DEMAN_INSTALL_PREFIX=${PREFIX} -DCMAKE_SKIP_RPATH=ON ${SRC_DIR}
elif [[ $OS == "mac" ]]; then
	cmake -DNUMPY_INCLUDE_PATH=${NPY_INC} -DPYTHON_INCLUDE_PATH=${PY_INC} -DEMAN_INSTALL_PREFIX=${PREFIX} -DCMAKE_SKIP_RPATH=ON $SRC_DIR
fi

make -j"$(bc -l <<< ${CPU_COUNT}-2)"
make install

