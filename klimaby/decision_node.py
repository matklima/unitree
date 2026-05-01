import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32

class DecisionNode(Node):
    def __init__(self):
        super().__init__('decision_node')
        
        # Pretplata na tvoj stabilni perception
        self.subscription = self.create_subscription(
            String, '/perception_state', self.decision_callback, 10)
            
        # Publisher prema actuation node-u (šaljemo ID stanja)
        self.publisher_ = self.create_publisher(Int32, '/robot_state', 10)
        
        # Pragovi (metri) - prilagodi ih po potrebi
        self.SAFE_DIST = 1.2    # Ispod ovoga počni skretati
        self.CRITICAL_DIST = 0.5 # Ispod ovoga stani (EMERGENCY)

    def decision_callback(self, msg):
        # Parsiranje podataka "N:L:D"
        try:
            parts = msg.data.split(':')
            f_dist = float(parts[0])
            l_dist = float(parts[1])
            r_dist = float(parts[2])
        except (ValueError, IndexError):
            return

        state = Int32()
        
        # LOGIKA ODLUČIVANJA
        if f_dist < self.CRITICAL_DIST:
            state.data = 0  # EMERGENCY STOP
            self.get_logger().warn("!!! PREBLIZU - STOP !!!")
            
        elif f_dist < self.SAFE_DIST or r_dist < 1.0:
            # Ako je zid ispred ILI desno (kao na slici), skreći lijevo
            state.data = 2  # TURN LEFT
            self.get_logger().info(f"Izbjegavam zid (N:{f_dist:.2f}, D:{r_dist:.2f}) -> SKREĆEM LIJEVO")
            
        else:
            state.data = 1  # FORWARD
            self.get_logger().info("Put je čist -> IDEM NAPRIJED")

        self.publisher_.publish(state)

def main():
    rclpy.init()
    node = DecisionNode()
    rclpy.spin(node)
    rclpy.shutdown()