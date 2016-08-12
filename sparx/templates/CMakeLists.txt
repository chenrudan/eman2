FILE(GLOB sxtemplates "${CMAKE_CURRENT_SOURCE_DIR}/*.py")

INSTALL(PROGRAMS ${sxtemplates}
  	DESTINATION    ${EMAN_INSTALL_PREFIX}/sparx/templates
)
