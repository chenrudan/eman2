FILE(GLOB pmfiles "${CMAKE_CURRENT_SOURCE_DIR}/*.*")
INSTALL(FILES ${pmfiles}
	DESTINATION    lib/python2.7/site-packages/EMAN2/pmconfig
)
