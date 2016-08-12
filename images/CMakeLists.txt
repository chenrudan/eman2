ADD_SUBDIRECTORY(macimages)

FILE(GLOB pngfiles "${CMAKE_CURRENT_SOURCE_DIR}/*.png")
FILE(GLOB icofiles "${CMAKE_CURRENT_SOURCE_DIR}/*.ico")
INSTALL(FILES ${pngfiles} ${icofiles}
  	DESTINATION    ${EMAN_INSTALL_PREFIX}/images
)

INSTALL(FILES Close.txt DESTINATION ${EMAN_INSTALL_PREFIX}/images)

# FIXING libpng warning: iCCP: known incorrect sRGB profile
# http://tex.stackexchange.com/questions/125612/warning-pdflatex-libpng-warning-iccp-known-incorrect-srgb-profile
