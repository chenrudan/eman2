#!/bin/bash

echo "Performing pre-linking tasks..."

ACTIVATE="${PREFIX}/etc/conda/activate.d"
DEACTIVATE="${PREFIX}/etc/conda/deactivate.d"
VARS="env_vars.sh"

mkdir -p "${ACTIVATE}"
touch "${ACTIVATE}/${VARS}"
if ! grep -q "/bin/bash" "${ACTIVATE}/${VARS}"; then
cat << EOF > "${ACTIVATE}/${VARS}"
#!/bin/bash
export EMAN2DIR=${PREFIX}
EOF
else
	echo "export EMAN2DIR=${PREFIX}" >> "${ACTIVATE}/${VARS}"
fi

mkdir -p "${DEACTIVATE}"
touch "${DEACTIVATE}/${VARS}"
if ! grep -q "/bin/bash" "${DEACTIVATE}/${VARS}"; then
cat << EOF > "${DEACTIVATE}/${VARS}"
#!/bin/bash
unset EMAN2DIR
EOF
else
	echo "unset EMAN2DIR" >> "${DEACTIVATE}/${VARS}"
fi
