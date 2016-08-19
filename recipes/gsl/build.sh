if [[ "$(uname)" == "Darwin" ]]; then
  # CC=clang otherwise:
  # error: ambiguous instructions require an explicit suffix
  # (could be 'filds', or 'fildl')
  # https://gcc.gnu.org/bugzilla/show_bug.cgi?id=66509
  export CC="clang"
fi

export CFLAGS="-I$PREFIX/include"
export CPPFLAGS="-I$PREFIX/include"
export CXXFLAGS="-I$PREFIX/include"
export LDFLAGS="-L$PREFIX/lib"

./configure --prefix=$PREFIX --enable-shared --disable-static --with-pic

make -j 2
make check || true
make install

