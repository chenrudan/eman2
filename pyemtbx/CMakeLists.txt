FILE(GLOB tbxprograms "${CMAKE_CURRENT_SOURCE_DIR}/*.py")
INSTALL(FILES ${tbxprograms}
  	DESTINATION    ${EMAN_INSTALL_PREFIX}/EMAN2/pyemtbx
)
INSTALL(FILES ${tbxprograms}
  	DESTINATION    ${EMAN_INSTALL_PREFIX}/sparx/pyemtbx
)
