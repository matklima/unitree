import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class ActuationNode(Node):
    def __init__(self):
        super().__init__('actuation_node')

        # Parametri za brzinu - omogućuju lakše podešavanje bez mijenjanja koda
        self.declare_parameter('linear_velocity', 0.2)   # m/s
        self.declare_parameter('angular_velocity', 1.0)  # rad/s

        # Publisher prema robotu (Gazebo cmd_vel)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Subscriber na odluke iz decision_node-a
        self.subscription = self.create_subscription(
            String,
            '/motion_command',
            self.command_callback,
            10
        )

        self.get_logger().info("Actuation Node spreman i čeka komande...")

    def command_callback(self, msg):
        try:
            parts = msg.data.split(':')
            command = parts[0]
            dist = float(parts[1])
        except: return

        twist = Twist()
        v_max = self.get_parameter('linear_velocity').value # npr. 0.3
        
        if command == 'slow_approach':
            # Povećaj donju granicu na 0.4 (40% snage) umjesto 0.1
            scale = (dist - 0.45) / (1.5 - 0.45)
            scale = max(0.4, min(scale, 1.0)) # 0.4 osigurava da se robot zapravo miče
            
            twist.linear.x = v_max * scale
            twist.angular.z = 0.0
            self.get_logger().info(f"Usporavam: v={twist.linear.x:.2f} (scale={scale:.2f})")

        elif command == 'turn_right' or command == 'turn_left':
            # Umjesto 0.0, daj mu malu linearnu brzinu da "izvuče" skretanje
            twist.linear.x = v_max * 0.5  # npr. pola maksimalne brzine
            
            # Smjer rotacije
            if command == 'turn_right':
                twist.angular.z = -0.8
            else:
                twist.angular.z = 0.8
                
            self.get_logger().info(f"Skrećem i bježim: v={twist.linear.x:.2f}, w={twist.angular.z:.2f}")

        elif command == 'move_forward':
            twist.linear.x = v_max
            twist.angular.z = 0.0
            
        elif command == 'stop':
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        self.cmd_vel_pub.publish(twist)

    def stop_robot(self):
        self.get_logger().info("Zaustavljam robota prije gašenja...")
        stop_msg = Twist()
        stop_msg.linear.x = 0.0
        stop_msg.angular.z = 0.0
        
        # Šaljemo poruku više puta da budemo sigurni da je Gazebo "ulovi"
        for _ in range(5):
            self.cmd_vel_pub.publish(stop_msg)
            import time
            time.sleep(0.05)

def main(args=None):
    rclpy.init(args=args)
    node = ActuationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Čim stisneš Ctrl+C u terminalu, poziva se stop_robot
        node.stop_robot() 
    finally:
        # Osiguravamo da robot stane čak i ako dođe do neočekivane greške
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()