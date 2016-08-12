#!/bin/sh

# to generate Doxygen documentation under eman2/doc
# usage: makedoc.sh

which doxygen 2>/dev/null 1>/dev/null
if test ! $? = 0; then
    echo
    echo "Error: 'doxygen' is not found. Please install 'doxgen' first"
    echo
    exit 1
fi

echo -n "Start to generate Doxygen documentation. Be patient ... "
doxygen  doxygen/Doxyfile
echo "Done"

echo "Documentation is at $PWD/doc/html/index.html"
