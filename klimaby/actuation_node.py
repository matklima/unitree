import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist

class ActuationNode(Node):
    def __init__(self):
        super().__init__('actuation_node')
        
        # Pretplata na odluku iz decision_node
        self.subscription = self.create_subscription(
            Int32, '/robot_state', self.listener_callback, 10)
            
        # Publisher za brzinu robota
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Definiramo brzine
        self.linear_speed = 0.3   # Brzina hoda naprijed
        self.rotation_speed = 0.6 # Brzina okretanja u mjestu

    def listener_callback(self, msg):
        twist = Twist()
        
        if msg.data == 1: # FORWARD
            twist.linear.x = self.linear_speed
            twist.angular.z = 0.0
            self.get_logger().info("HODAM: Naprijed")
            
        elif msg.data == 2: # TURN LEFT (U mjestu)
            twist.linear.x = 0.0      # Zaustavi hod
            twist.angular.z = self.rotation_speed # Rotiraj se
            self.get_logger().info("ROTACIJA: Skrećem u mjestu ulijevo")
            
        else: # STOP (State 0 ili bilo što drugo)
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.get_logger().warn("STOP: Mirujem")

        self.publisher_.publish(twist)

def main():
    rclpy.init()
    node = ActuationNode()
    rclpy.spin(node)
    rclpy.shutdown()