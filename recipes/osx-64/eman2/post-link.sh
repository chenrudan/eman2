echo "Performing post-linking tasks..."

python fixlibs.py --os=mac --root=${PREFIX} --version=${GIT_BUILD_STR} --arch=${ARCH}
