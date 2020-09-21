cmake_minimum_required(VERSION 3.16)
project(fld_pyutils CXX)
set(CMAKE_CXX_STANDARD 14)

#add_subdirectory(contrib/vtk)

find_package(VTK REQUIRED)
vtk_module_config(VTK
        vtkCommonCore
        vtkFiltersSources
        vtkInteractionStyle
        vtkInteractionWidgets
        vtkRenderingOpenGL2
        vtkRenderingLOD
        vtkIOParallel
        )
include(${VTK_USE_FILE})

#add_executable(my_cylinder my_cylinder.cpp)
#target_link_libraries(my_cylinder ${VTK_LIBRARIES})

add_executable(main cxx/src/main.cpp)
target_link_libraries(main PUBLIC ${VTK_LIBRARIES})
target_include_directories(main PUBLIC cxx/include)

add_executable(plot_hex_grid cxx/src/plot_hex_grid.cpp)
target_link_libraries(plot_hex_grid PUBLIC ${VTK_LIBRARIES})
target_include_directories(plot_hex_grid PUBLIC cxx/include)
