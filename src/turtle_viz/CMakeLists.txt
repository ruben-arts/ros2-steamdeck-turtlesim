cmake_minimum_required(VERSION 3.8)
project(turtle_viz)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(turtlesim REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2 REQUIRED)

add_executable(turtle_viz_node src/turtle_viz_node.cpp)
ament_target_dependencies(turtle_viz_node
  rclcpp turtlesim nav_msgs geometry_msgs visualization_msgs tf2_ros tf2)

install(TARGETS turtle_viz_node DESTINATION lib/${PROJECT_NAME})

ament_package()
