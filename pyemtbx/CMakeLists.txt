FILE(GLOB tbxprograms "${CMAKE_CURRENT_SOURCE_DIR}/*.py")
INSTALL(FILES ${tbxprograms}
  	DESTINATION    lib/python2.7/site-packages/EMAN2/pyemtbx
)
