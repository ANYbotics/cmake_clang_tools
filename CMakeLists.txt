cmake_minimum_required(VERSION 3.5.1)
project(cmake_clang_tools)

# Installation paths
set(PYTHON_SCRIPTS_INSTALL_PATH ${CMAKE_INSTALL_PREFIX}/bin)
set(CONFIG_FILES_INSTALL_PATH ${CMAKE_INSTALL_PREFIX}/share/cmake_clang_tools)
set(CMAKE_SCRIPTS_INSTALL_PATH ${CONFIG_FILES_INSTALL_PATH})

# Register the local build in case one doesn't use "make install"
export(PACKAGE cmake_clang_tools)

# ... for the build tree
set(PYTHON_SCRIPTS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/bin")
set(CONFIG_FILE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/config")
configure_file(cmake/cmake_clang_tools-macros.cmake.in
  "${PROJECT_BINARY_DIR}/cmake_clang_tools-macros.cmake" @ONLY)

set(CMAKE_CLANG_TOOLS_MACROS_PATH ${PROJECT_BINARY_DIR})
configure_file(cmake/cmake_clang_toolsConfig.cmake.in
  "${PROJECT_BINARY_DIR}/cmake_clang_toolsConfig.cmake" @ONLY)

# ... for the install tree
set(PYTHON_SCRIPTS_DIR "${PYTHON_SCRIPTS_INSTALL_PATH}")
set(CONFIG_FILE_DIR "${CONFIG_FILES_INSTALL_PATH}")
configure_file(cmake/cmake_clang_tools-macros.cmake.in
  "${PROJECT_BINARY_DIR}/cmake_clang_tools-macros.cmake" @ONLY)

set(CMAKE_CLANG_TOOLS_MACROS_PATH ${CMAKE_SCRIPTS_INSTALL_PATH})
configure_file(cmake/cmake_clang_toolsConfig.cmake.in
  "${PROJECT_BINARY_DIR}/cmake_clang_toolsConfig.cmake" @ONLY)

# Install scripts, configurations and CMake files.
install(
  FILES
    bin/check_if_tool_runs.py
    bin/cmake_clang_tools_helpers.py
    bin/run_clang_format_tool.py
    bin/run_clang_tidy_tool.py
  DESTINATION ${PYTHON_SCRIPTS_INSTALL_PATH}
  PERMISSIONS WORLD_EXECUTE WORLD_READ GROUP_EXECUTE GROUP_READ OWNER_EXECUTE OWNER_WRITE OWNER_READ
)

install(
  FILES
    config/.clang-format
    config/.clang-tidy
    config/config.yaml
  DESTINATION ${CONFIG_FILES_INSTALL_PATH}
  PERMISSIONS WORLD_READ GROUP_READ OWNER_WRITE OWNER_READ
)

install(
  FILES
    "${PROJECT_BINARY_DIR}/cmake_clang_toolsConfig.cmake"
    "${PROJECT_BINARY_DIR}/cmake_clang_tools-macros.cmake"
  DESTINATION ${CMAKE_SCRIPTS_INSTALL_PATH}
)

install(
  FILES package.xml
  DESTINATION ${CONFIG_FILES_INSTALL_PATH}
)

# Uninstall
configure_file("${CMAKE_CURRENT_SOURCE_DIR}/cmake/cmake_uninstall.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
    IMMEDIATE @ONLY
)

add_custom_target(uninstall
  COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake
)

# Testing
# Attach the target to ALL to always run the tests.
# This is not a catkin package and there is no way to run them otherwise.
add_custom_target(test_${PROJECT_NAME} ALL
  COMMAND pytest-3 ${CMAKE_SOURCE_DIR}/test
)