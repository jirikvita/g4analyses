cmake_minimum_required(VERSION 3.16)
project(timepix)

find_package(Geant4 REQUIRED ui_all vis_all)
include(${Geant4_USE_FILE})

add_executable(timepix timepix.cpp)
target_link_libraries(timepix ${Geant4_LIBRARIES})
