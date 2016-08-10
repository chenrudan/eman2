#!/bin/bash

case "$(uname -s)" in
        Darwin*)  OS="mac" ;;
        Linux*)   OS="linux" ;;
        *)        OS="other" ;;
esac

if [[ $OS == "linux" ]]; then
	## requires: freeglut, libgl1-mesa-dev
	./configure --prefix=$PREFIX --enable-shared LIBS="-lGL -lGLU -lm -ldl -lXxf86vm -lpthread"
elif [[ $OS == "mac" ]]; then
	./configure --prefix=$PREFIX --enable-shared
fi

make -j"$(bc -l <<< ${CPU_COUNT}-2)"
make check
make install

