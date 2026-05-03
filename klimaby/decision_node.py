import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32
from enum import IntEnum
from rcl_interfaces.msg import SetParametersResult


# 1. Definiramo stanja kao Enum radi čitljivosti
class RobotState(IntEnum):
    STOP = 0
    FORWARD = 1
    LEFT = 2
    RIGHT = 3

class DecisionNode(Node):
    def __init__(self):
        super().__init__('decision_node')

        self.forced_turn_steps = 0
        self.current_action = RobotState.STOP
        self.safety_mode_active = False

        self.declare_parameter('safe_dist', 1.2)
        self.declare_parameter('critical_dist', 0.5)
        self.declare_parameter('side_threshold', 1.0)
        self.declare_parameter('long_turn_steps', 15)
        self.declare_parameter('short_turn_steps', 8)

        self.safe_dist = self.get_parameter('safe_dist').value
        self.critical_dist = self.get_parameter('critical_dist').value
        self.side_threshold = self.get_parameter('side_threshold').value
        self.long_turn_steps = self.get_parameter('long_turn_steps').value
        self.short_turn_steps = self.get_parameter('short_turn_steps').value

        self.add_on_set_parameters_callback(self.parameter_callback)

        self.subscription = self.create_subscription(
            String, '/perception_state', self.decision_callback, 10)
        self.publisher_ = self.create_publisher(Int32, '/robot_state', 10)
        self.last_update_time = self.get_clock().now()

        self.safety_timer = self.create_timer(0.1, self.safety_check)

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'safe_dist':
                if param.value <= 0: return SetParametersResult(successful=False, reason="Udaljenost mora biti > 0")
                self.safe_dist = param.value
            elif param.name == 'critical_dist':
                self.critical_dist = param.value
            elif param.name == 'side_threshold':
                self.side_threshold = param.value
            elif param.name == 'long_turn_steps':
                self.long_turn_steps = param.value
            elif param.name == 'short_turn_steps':
                self.short_turn_steps = param.value
                
        self.get_logger().info("Parametri uspješno ažurirani!")
        return SetParametersResult(successful=True)

    def safety_check(self):
        # Ako poruka kasni više od 0.5 sekundi, gasi motore
        elapsed = self.get_clock().now() - self.last_update_time
        if elapsed.nanoseconds > 0.5 * 1e9:
            if not self.safety_mode_active:
                self.get_logger().error("Perception node izgubljen: Zaustavljam robota!")
                self.safety_mode_active = True
            
            state = Int32()
            state.data = RobotState.STOP
            self.publisher_.publish(state)

    def decision_callback(self, msg):
        if self.safety_mode_active:
            self.get_logger().info("RECOVERY: Perception node ponovno aktivan. Nastavljam s radom.")
            self.safety_mode_active = False

        self.last_update_time = self.get_clock().now()
        
        distances = self.parse_perception(msg.data)
        if not distances:
            return
        
        f_dist, l_dist, r_dist = distances
        state = Int32()

        # LOGIKA ODLUČIVANJA
        
        if self.forced_turn_steps > 0:
            self.forced_turn_steps -= 1
            state.data = self.current_action
        
        # B. Emergency situacija (Kritično blizu)
        elif f_dist < self.critical_dist:
            self.get_logger().warn("!!! BLIZINA: Rotacija u mjestu !!!")
            if l_dist > r_dist:
                self.current_action = RobotState.LEFT
            else:
                self.current_action = RobotState.RIGHT            
            self.forced_turn_steps = self.long_turn_steps
            state.data = self.current_action

        # C. Izbjegavanje ispred (Safe distance)
        elif f_dist < self.safe_dist:
            if l_dist > r_dist:
                self.current_action = RobotState.LEFT
                self.get_logger().info("Izbjegavam frontalno -> LIJEVO")
            else:
                self.current_action = RobotState.RIGHT
                self.get_logger().info("Izbjegavam frontalno -> DESNO")
            self.forced_turn_steps = self.long_turn_steps
            state.data = self.current_action

        # D. Bočno izbjegavanje
        elif r_dist < self.side_threshold or l_dist < self.side_threshold:
            if l_dist > r_dist:
                self.current_action = RobotState.LEFT
            else:
                self.current_action = RobotState.RIGHT
            self.forced_turn_steps = self.short_turn_steps
            state.data = self.current_action

        # E. Put je čist
        else:
            self.current_action = RobotState.FORWARD
            state.data = self.current_action
        
        self.publisher_.publish(state)

    def parse_perception(self, data):
        try:
            parts = data.split(':')
            return [float(p) for p in parts]
        except (ValueError, IndexError):
            self.get_logger().error("Neuspjelo parsiranje percepcije!")
            return None

def main():
    rclpy.init()
    node = DecisionNode()
    rclpy.spin(node)
    rclpy.shutdown()