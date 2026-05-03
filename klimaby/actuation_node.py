import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
from enum import IntEnum

class RobotState(IntEnum):
    STOP = 0
    FORWARD = 1
    LEFT = 2
    RIGHT = 3

class ActuationNode(Node):
    def __init__(self):
        super().__init__('actuation_node')
        
        # 1. Parameters with local variables
        self.declare_parameter('linear_speed', 0.3)
        self.declare_parameter('rotation_speed', 0.3)
        self.declare_parameter('accel_limit', 0.05) # How much speed can change in one step

        self.lin_vel_target = self.get_parameter('linear_speed').value
        self.rot_vel_target = self.get_parameter('rotation_speed').value
        self.accel_limit = self.get_parameter('accel_limit').value
        
        self.fail_safe_active = False

        # 2. Current speeds (for smooth transition)
        self.current_linear = 0.0
        self.current_angular = 0.0
        
        # 3. Callback for parameters
        self.add_on_set_parameters_callback(self.parameter_callback)
            
        self.subscription = self.create_subscription(
            Int32, '/robot_state', self.state_callback, 10)
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.current_state = RobotState.STOP
        self.last_msg_time = self.get_clock().now()
        self.timer = self.create_timer(0.1, self.control_loop)

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'linear_speed': self.lin_vel_target = param.value
            elif param.name == 'rotation_speed': self.rot_vel_target = param.value
            elif param.name == 'accel_limit': self.accel_limit = param.value
        return SetParametersResult(successful=True)

    def state_callback(self, msg):
        try:
            self.current_state = RobotState(msg.data)
        except ValueError:
            self.current_state = RobotState.STOP
        self.last_msg_time = self.get_clock().now()

    def control_loop(self):
        # Watchdog check
        elapsed = self.get_clock().now() - self.last_msg_time
        
        if elapsed.nanoseconds > 0.5 * 1e9:
            # If this is the first time we detect a loss, print error
            if not self.fail_safe_active:
                self.get_logger().error("FAIL-SAFE: Decision node lost! Stopping robot.")
                self.fail_safe_active = True
            
            self.current_state = RobotState.STOP
        else:
            # RECOVERY LOGIC: If messages have started coming again
            if self.fail_safe_active:
                self.get_logger().info("RECOVERY: Connection with Decision node re-established.")
                self.fail_safe_active = False

        # Define target speeds for this cycle
        target_lin = 0.0
        target_ang = 0.0

        if self.current_state == RobotState.FORWARD:
            target_lin = self.lin_vel_target
        elif self.current_state == RobotState.LEFT:
            target_ang = self.rot_vel_target
        elif self.current_state == RobotState.RIGHT:
            target_ang = -self.rot_vel_target

        # RAMPING LOGIC: Gradually approach target speed
        self.current_linear = self.smooth_value(self.current_linear, target_lin)
        self.current_angular = self.smooth_value(self.current_angular, target_ang)

        msg = Twist()
        msg.linear.x = self.current_linear
        msg.angular.z = self.current_angular
        self.publisher_.publish(msg)

    def smooth_value(self, current, target):
        # Simple linear ramp
        diff = target - current
        if abs(diff) < self.accel_limit:
            return target
        return current + (self.accel_limit if diff > 0 else -self.accel_limit)

def main():
    rclpy.init()
    node = ActuationNode()
    rclpy.spin(node)
    rclpy.shutdown()