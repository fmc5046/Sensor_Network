cmake_minimum_required(VERSION 3.19)
project(mi LANGUAGES C)
if(CMAKE_BUILD_TYPE STREQUAL "Test")
  set(CMAKE_BUILD_TYPE "Debug")
  if(CMAKE_C_COMPILER_ID STREQUAL "GNU")
    find_program(LCOV_BIN lcov)
    if(LCOV_BIN MATCHES "lcov$")
      set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} --coverage -fprofile-arcs -ftest-coverage")
    else()
      message("Not producing code coverage information since lcov was not found")
    endif()
  else()
    message("Not producing code coverage information since the selected compiler is no gcc")
  endif()
endif()
# Require C11
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
# Require C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(DEFAULT_BUILD_TYPE Release)
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE ${DEFAULT_BUILD_TYPE} CACHE STRING "Choose the type of build." FORCE)
endif()
# do not print install messages
set(CMAKE_INSTALL_MESSAGE NEVER)
# Target definitions
add_compile_definitions(LF_REACTION_GRAPH_BREADTH=6)
add_compile_definitions(LF_UNTHREADED=1)
add_compile_definitions(LOG_LEVEL=2)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
add_compile_definitions(_LF_GARBAGE_COLLECTED)
add_subdirectory(core)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR})
set(LF_MAIN_TARGET LinguaFrancami)
find_package(Python 3.7.0...<3.11.0 COMPONENTS Interpreter Development)
Python_add_library(
    ${LF_MAIN_TARGET}
    MODULE
    lib/schedule.c
    lib/python_action.c
    lib/python_port.c
    lib/python_tag.c
    lib/python_time.c
    lib/pythontarget.c
    mi.c
)
if (MSVC)
    set_target_properties(${LF_MAIN_TARGET} PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR})
    set_target_properties(${LF_MAIN_TARGET} PROPERTIES LIBRARY_OUTPUT_DIRECTORY_DEBUG ${CMAKE_SOURCE_DIR})
    set_target_properties(${LF_MAIN_TARGET} PROPERTIES LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_SOURCE_DIR})
    set_target_properties(${LF_MAIN_TARGET} PROPERTIES LIBRARY_OUTPUT_DIRECTORY_MINSIZEREL ${CMAKE_SOURCE_DIR})
    set_target_properties(${LF_MAIN_TARGET} PROPERTIES LIBRARY_OUTPUT_DIRECTORY_RELWITHDEBINFO ${CMAKE_SOURCE_DIR})
endif (MSVC)
set_target_properties(${LF_MAIN_TARGET} PROPERTIES PREFIX "")
include_directories(${Python_INCLUDE_DIRS})
target_link_libraries(${LF_MAIN_TARGET} PRIVATE ${Python_LIBRARIES})
target_compile_definitions(${LF_MAIN_TARGET} PUBLIC MODULE_NAME=LinguaFrancami)
target_link_libraries(${LF_MAIN_TARGET} PRIVATE core)
target_include_directories(${LF_MAIN_TARGET} PUBLIC include/)
target_include_directories(${LF_MAIN_TARGET} PUBLIC include/api)
target_include_directories(${LF_MAIN_TARGET} PUBLIC include/core)
target_include_directories(${LF_MAIN_TARGET} PUBLIC include/core/platform)
target_include_directories(${LF_MAIN_TARGET} PUBLIC include/core/modal_models)
target_include_directories(${LF_MAIN_TARGET} PUBLIC include/core/utils)
# Set flag to indicate a single-threaded runtime
target_compile_definitions( ${LF_MAIN_TARGET} PUBLIC LF_UNTHREADED=1)
set(CMAKE_C_COMPILER gcc)
install(TARGETS)
