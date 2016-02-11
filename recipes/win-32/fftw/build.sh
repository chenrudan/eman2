#!/usr/bin/env bash
# inspired by build script for Arch Linux fftw pacakge:
# https://projects.archlinux.org/svntogit/packages.git/tree/trunk/PKGBUILD?h=packages/fftw

# Single precision (fftw libraries have "f" suffix)
./configure --prefix=$PREFIX --enable-shared --enable-float 
make
make install

# Test suite
# tests are performed during building as they are not available in the
# installed package.
# Additional tests can be run with make smallcheck and make bigcheck
#cd tests && make check-local
# Additional tests can be run using the next two lines
#make smallcheck
#make bigcheck

