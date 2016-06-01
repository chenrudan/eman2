#!/bin/bash

echo "Removing EMAN2 from current environment"

#ACTIVATE="${PREFIX}/etc/conda/activate.d"
#DEACTIVATE="${PREFIX}/etc/conda/deactivate.d"

#AVARS="${ACTIVATE}/env_vars.sh"
#DVARS="${DEACTIVATE}/env_vars.sh"

#echo "Removing environment variable definitions"
#
#if [ -f $AVARS ]; then
#	grep -v "EMAN2DIR" ${AVARS} > ${AVARS/.sh/.tmp} && mv -f ${AVARS/.sh/.tmp} ${AVARS}
#	grep -v "LD_LIBRARY_PATH" ${AVARS} > ${AVARS/.sh/.tmp} && mv -f ${AVARS/.sh/.tmp} ${AVARS}
#fi
#
#if [ -f $DVARS ]; then
#	grep -v "EMAN2DIR" ${DVARS} > ${AVARS/.sh/.tmp} && mv -f ${AVARS/.sh/.tmp} ${DVARS}
#	grep -v "LD_LIBRARY_PATH" ${DVARS} > ${AVARS/.sh/.tmp} && mv -f ${AVARS/.sh/.tmp} ${DVARS}
#fi

echo "Removing symbolically linked libraries"

cd ${PREFIX}/lib/python2.7/site-packages/EMAN2

for i in $(ls *.so); do
	#echo "REMOVING: ${PREFIX}/lib/${i}"
	rm -f ${PREFIX}/lib/$i
done

cd ${PREFIX}

rm -f ${PREFIX}/eman2.info

