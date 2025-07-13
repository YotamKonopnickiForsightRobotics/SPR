cmake_minimum_required(VERSION 3.10)
project(YourProject)

set(CMAKE_CXX_STANDARD 17)

# Add GLFW (rename this if your actual folder is named differently)
add_subdirectory(glfw)

# Include headers
include_directories(
        ${CMAKE_CURRENT_SOURCE_DIR}/imgui
        ${CMAKE_CURRENT_SOURCE_DIR}/imgui/backends
        ${CMAKE_CURRENT_SOURCE_DIR}/glfw/include
)

# Find OpenGL
find_package(OpenGL REQUIRED)

# Source files
set(SOURCES
        main.cpp
        imgui/imgui.cpp
        imgui/imgui_draw.cpp
        imgui/imgui_tables.cpp
        imgui/imgui_widgets.cpp
        imgui/imgui_demo.cpp
        imgui/backends/imgui_impl_glfw.cpp
        imgui/backends/imgui_impl_opengl3.cpp
)

set(CMAKE_EXE_LINKER_FLAGS "-static")

# Create executable
add_executable(${PROJECT_NAME} ${SOURCES})

set_target_properties(${PROJECT_NAME} PROPERTIES WIN32_EXECUTABLE TRUE)

# Link everything
target_link_libraries(${PROJECT_NAME}
        glfw
        OpenGL::GL
)
