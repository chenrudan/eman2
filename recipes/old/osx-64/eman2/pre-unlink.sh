#!/bin/bash

echo "Removing EMAN2 from current environment"

ACTIVATE="${PREFIX}/etc/conda/activate.d"
DEACTIVATE="${PREFIX}/etc/conda/deactivate.d"

AVARS="${ACTIVATE}/env_vars.sh"
DVARS="${DEACTIVATE}/env_vars.sh"

grep -v "EMAN2DIR" ${AVARS} > ${AVARS/.sh/.tmp} && mv -f ${AVARS/.sh/.tmp} ${AVARS}
grep -v "EMAN2DIR" ${DVARS} > ${AVARS/.sh/.tmp} && mv -f ${AVARS/.sh/.tmp} ${DVARS}
