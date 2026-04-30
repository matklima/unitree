import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class DecisionNode(Node):
    def __init__(self):
        super().__init__('decision_node')
        
        # Slušamo nove "F:L:R" podatke
        self.sub = self.create_subscription(String, '/perception_state', self.callback, 10)
        self.pub = self.create_publisher(String, '/motion_command', 10)
        
        self.avoidance_counter = 0
        self.chosen_direction = "turn_left"
        self.get_logger().info("Decision Node spreman. Čekam F:L:R podatke...")

    def callback(self, msg):
        try:
            parts = msg.data.split(':')
            f_dist = float(parts[0])
            l_dist = float(parts[1])
            r_dist = float(parts[2])
        except (ValueError, IndexError):
            return

        # Pragovi (podesi prema svom robotu)
        STOP_THRESHOLD = 0.75  # POVEĆANO: Ako je prepreka bliže od 75cm, odmah skreći
        SLOW_THRESHOLD = 1.5   # Sve između 0.75m i 1.5m je usporavanje

        if f_dist < STOP_THRESHOLD:
            # Umjesto da dopustimo robotu da dođe na 0.4m i stane, 
            # čim dođe na 0.75m prisiljavamo ga na skretanje.
            if r_dist > l_dist:
                cmd = f"turn_right:{f_dist}"
            else:
                cmd = f"turn_left:{f_dist}"
            self.get_logger().info(f"Izbjegavam: {cmd}")

        elif f_dist < SLOW_THRESHOLD:
            # Ovdje dodajemo MINIMALNU brzinu
            # Čak i ako je robot blizu, ne dajemo mu da ide sporije od npr. 0.15 m/s
            cmd = f"slow_approach:{f_dist}"
                
        else:
            # Put je čist
            cmd = f"move_forward:{f_dist}"

        self.pub.publish(String(data=cmd))

def main(args=None):
    rclpy.init(args=args)
    node = DecisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()