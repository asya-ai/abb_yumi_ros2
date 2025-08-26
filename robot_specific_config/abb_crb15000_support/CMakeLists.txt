cmake_minimum_required(VERSION 3.5)
project(abb_crb15000_support)

find_package(ament_cmake REQUIRED)

find_package(xacro REQUIRED)
find_package(robot_state_publisher REQUIRED)

install(
  DIRECTORY config launch meshes urdf
  DESTINATION share/${PROJECT_NAME}
)

install(
  FILES LICENSE
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
