import sys
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import Pose
from std_msgs.msg import Header
from shape_msgs.msg import SolidPrimitive
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    MotionPlanRequest,
    Constraints,
    PositionConstraint,
    PlanningOptions,
    WorkspaceParameters,
)
from builtin_interfaces.msg import Duration


class MoveToXYZ(Node):
    def __init__(self):
        super().__init__('left_arm_xyz_client')

        # MoveGroup action (default name exposed by move_group)
        self._client = ActionClient(self, MoveGroup, 'move_action')

        # Parameters (you can also turn these into ROS params if you want)
        self.group_name = 'left_arm'          # from your SRDF
        self.ee_link = 'grpl_base'            # end effector link (tip) from your SRDF
        self.ref_frame = 'world'              # use 'world' since SRDF defines a world joint
        self.position_tolerance = 0.005       # meters, sphere radius around target
        self.allowed_planning_time = 5.0      # seconds
        self.velocity_scale = 0.3
        self.accel_scale = 0.3
        self.num_attempts = 1

    def go_to_xyz(self, x: float, y: float, z: float) -> bool:
        # Wait for action server
        if not self._client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('MoveGroup action server not available on /move_action')
            return False

        # --- Build a PositionConstraint to place ee_link at (x,y,z) within a small sphere ---
        header = Header()
        header.frame_id = self.ref_frame

        sphere = SolidPrimitive()
        sphere.type = SolidPrimitive.SPHERE
        sphere.dimensions = [self.position_tolerance]  # radius

        sphere_pose = Pose()
        sphere_pose.position.x = float(x)
        sphere_pose.position.y = float(y)
        sphere_pose.position.z = float(z)
        # orientation is irrelevant for a position constraint

        pos_constraint = PositionConstraint()
        pos_constraint.header = header
        pos_constraint.link_name = self.ee_link
        pos_constraint.constraint_region.primitives = [sphere]
        pos_constraint.constraint_region.primitive_poses = [sphere_pose]
        pos_constraint.weight = 1.0

        goal_constraints = Constraints()
        goal_constraints.position_constraints = [pos_constraint]
        # No orientation constraint -> orientation is free

        # --- Build the MotionPlanRequest ---
        req = MotionPlanRequest()
        req.group_name = self.group_name
        req.num_planning_attempts = self.num_attempts
        req.allowed_planning_time = self.allowed_planning_time
        req.max_velocity_scaling_factor = self.velocity_scale
        req.max_acceleration_scaling_factor = self.accel_scale
        req.goal_constraints = [goal_constraints]

        # Optional workspace (kept generous / defaulted)
        req.workspace_parameters = WorkspaceParameters()
        req.workspace_parameters.header = header

        # --- Planning options: execute after planning ---
        opts = PlanningOptions()
        opts.plan_only = False
        opts.look_around = False
        opts.replan = True
        opts.look_around_attempts = 0
        opts.max_safe_execution_cost = 0.0
        opts.replan_attempts = 1
        opts.replan_delay = 0.0

        goal = MoveGroup.Goal()
        goal.request = req
        goal.planning_options = opts

        # Send goal and wait for result
        self.get_logger().info(f'Planning & executing to XYZ: [{x:.3f}, {y:.3f}, {z:.3f}] in {self.ref_frame}')
        send_future = self._client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send_future)

        goal_handle = send_future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by MoveGroup')
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result().result

        # Check MoveIt error code
        code = result.error_code.val
        # 1 == SUCCESS per MoveIt error codes
        if code == 1:
            self.get_logger().info('Success: motion planned and executed.')
            return True
        else:
            self.get_logger().error(f'MoveIt failed with error code: {code}')
            return False


def main(argv: Optional[list] = None):
    rclpy.init(args=argv)
    node = MoveToXYZ()

    # Allow CLI usage: ros2 run ... left_arm_xyz_client -- x y z [frame]
    # Example: ros2 run yumi_moveit_actions left_arm_xyz_client -- 0.40 0.10 0.30 world
    if len(sys.argv) >= 4:
        x, y, z = float(sys.argv[-3]), float(sys.argv[-2]), float(sys.argv[-1])
        success = node.go_to_xyz(x, y, z)
    else:
        node.get_logger().info('Usage: left_arm_xyz_client.py X Y Z  (frame defaults to world)')
        success = False

    rclpy.shutdown()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
