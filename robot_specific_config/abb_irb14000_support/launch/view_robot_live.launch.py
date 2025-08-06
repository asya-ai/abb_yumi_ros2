import os
import xacro
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """Launch RViz that visualises the *live* /joint_states coming from the ABB driver.

    We deliberately **do not** start `joint_state_publisher_gui`, because that would
    publish synthetic joint states and overwrite the real robot data.
    """

    # ------------------------------------------------------------------
    # 1. Robot description (URDF via xacro)
    # ------------------------------------------------------------------
    support_pkg = "abb_irb14000_support"
    support_path = get_package_share_directory(support_pkg)

    xacro_file = os.path.join(support_path, "urdf", "irb14000.urdf.xacro")
    robot_description = {
        "robot_description": xacro.process_file(xacro_file).toxml()
    }

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],  # listens to /joint_states by default
    )

    # ------------------------------------------------------------------
    # 2. RViz configured for the YuMi model
    # ------------------------------------------------------------------
    rviz_config = os.path.join(support_path, "rviz", "urdf_description.rviz")
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config],
        output="screen",
    )

    # ------------------------------------------------------------------
    # Return the launch description without any fake joint-state sources
    # ------------------------------------------------------------------
    return LaunchDescription([
        robot_state_publisher_node,
        rviz_node,
    ])
