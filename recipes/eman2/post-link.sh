#!/bin/bash

#case "$(uname -s)" in
#  Darwin*)  OS="osx" ;; 
#  Linux*)   OS="linux" ;;
#  *)        OS="other" ;;
#esac
#
#case "$(uname -m)" in
#  x86_64)  ARCH="64" ;;
#  i686)    ARCH="32" ;;
#  *)       ARCH="other" ;;
#esac

#NAME="${PKG_NAME}-${PKG_VERSION}"
#FULLNAME="${NAME}-${PKG_BUILDNUM}"
#RECIPE="${PREFIX}/pkgs/${FULLNAME}/info/recipe"
#TARGET="${OS}-${ARCH}"
#DATE=$(date)

#echo "Writing installation information to ${PREFIX}/eman2.info"
#
#cat << EOF > "${PREFIX}/eman2.info"
#NAME: ${FULLNAME}
#DATE: ${DATE}
#CONDA: ${PREFIX}
#SYSTEM: ${TARGET}
#EOF

echo "Replacing EMAN2DIR environment variable with anaconda prefix"
grep -rl 'os.getenv("EMAN2DIR")' ${PREFIX} | xargs sed -i "s|os.getenv(\"EMAN2DIR\")|os.sys.prefix|g"

#echo "Fixing shared library links"
#python ${RECIPE}/fix-libs.py --target=${TARGET} --prefix=${PREFIX} --dist=${NAME}

echo "Linking EMAN2 shared objects to anaconda environment"
cd ${PREFIX}/lib/python2.7/site-packages/EMAN2
ln -s libEM2.so ${PREFIX}/lib
ln -s libGLEM2.so ${PREFIX}/lib
ln -s libpy*.so pyemtbx
cd ${PREFIX}

