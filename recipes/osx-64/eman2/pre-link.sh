#!/bin/bash

echo "Performing pre-linking tasks..."

case "$OSTYPE" in
  darwin*)  OS="mac" ;; 
  linux*)   OS="linux" ;;
  *)        OS="other" ;;
esac

ARCH=$(uname -m)

RECIPE="${PREFIX}/pkgs/${PKG_NAME}-${PKG_VERSION}-${PKG_BUILDNUM}/info/recipe"

python ${RECIPE}/fix-libs.py --os=${OS} --root=${PREFIX} --arch=${ARCH}
