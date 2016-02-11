
# REQUIREMENTS:
# - freeglut
# - libgl1-mesa-dev

./configure --prefix=$PREFIX --enable-shared LIBS="-lGL -lGLU -lm -ldl -lXxf86vm -lpthread"

make
make install

