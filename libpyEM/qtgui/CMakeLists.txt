FILE(GLOB qtguifiles "${CMAKE_CURRENT_SOURCE_DIR}/*.py")
FILE(GLOB exclusionlist "em3Dhelloworld.py")
LIST(REMOVE_ITEM qtguifiles ${exclusionlist})
INSTALL(FILES ${qtguifiles} DESTINATION ${CMAKE_INSTALL_PREFIX}/EMAN2/qtgui)

