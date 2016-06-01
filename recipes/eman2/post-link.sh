#!/bin/bash

echo "Performing post-linking tasks..."

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
DATE=$(date)

echo "Writing installation information to ${PREFIX}/eman2.info"

cat << EOF > "${PREFIX}/eman2.info"
EMAN2 Install Info:
DATE: ${DATE}
NAME: ${PKG_NAME}
VERSION: ${PKG_VERSION}
CONDA_ENV: ${PREFIX}
TARGET: ${TARGET}
EOF

echo "Replacing EMAN2DIR environment variable with anaconda prefix"

grep -rl 'os.getenv("EMAN2DIR")' ${PREFIX}/bin | xargs sed -i "s|os.getenv(\"EMAN2DIR\")|\""${PREFIX}"\"|g"
grep -rl 'os.getenv("EMAN2DIR")' ${PREFIX}/lib | xargs sed -i "s|os.getenv(\"EMAN2DIR\")|\""${PREFIX}"\"|g"

echo "Fixing shared library links"

python ${RECIPE}/fix-libs.py --target=${TARGET} --prefix=${PREFIX} --dist=${NAME}

echo "Linking EMAN2 shared objects to anaconda environment"

cd ${PREFIX}/lib
ln -s python2.7/site-packages/EMAN2/*.so .
cd ${PREFIX}

