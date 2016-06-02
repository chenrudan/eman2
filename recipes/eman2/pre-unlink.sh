#!/bin/bash

echo "Removing symbolically linked libraries"
cd ${PREFIX}/lib/python2.7/site-packages/EMAN2
for i in $(ls *.so); do
	unlink ./pyemtbx/$i
	unlink ${PREFIX}/lib/$i
done
cd ${PREFIX}

#echo "Removing installation information"
#rm -f ${PREFIX}/eman2.info

