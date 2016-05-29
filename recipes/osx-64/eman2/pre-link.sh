#!/bin/bash

echo "Performing pre-linking tasks..."

case "$(uname -s)" in
  Darwin*)  OS="osx" ;; 
  Linux*)   OS="linux" ;;
  *)        OS="other" ;;
esac

case "$(uname -m)" in
  x86_64)  ARCH="64" ;;
  i686)    ARCH="32" ;;
  *)       ARCH="other" ;;
esac

NAME="${PKG_NAME}-${PKG_VERSION}"
FULLNAME="${NAME}-${PKG_BUILDNUM}"
RECIPE="${PREFIX}/pkgs/${FULLNAME}/info/recipe"
TARGET="${OS}-${ARCH}"

echo "Installing ${NAME} to ${PREFIX} on ${TARGET} ($(date))"

python ${RECIPE}/fix-libs.py --target=${TARGET} --prefix=${PREFIX} --dist=${NAME}
