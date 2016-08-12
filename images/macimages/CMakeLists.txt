FILE(GLOB pngfiles "${CMAKE_CURRENT_SOURCE_DIR}/*.png")
INSTALL(FILES ${pngfiles} 
  	DESTINATION    ${EMAN_INSTALL_PREFIX}/images/macimages
)
