import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
import math

class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')
        # Povišen prag detekcije na 1.0m za stabilnije izbjegavanje
        self.declare_parameter('threshold', 1.0) 
        
        self.pub = self.create_publisher(String, '/perception_state', 10)
        self.sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        
        self.get_logger().info("Perception Node pokrenut. Filtriram sve ispod 0.7m (tijelo robota).")

    def get_dist(self, data):
        # Donja granica 0.5m (iznad koljena robota), gornja 3.5m (limit senzora)
        clean = [r for r in data if 0.5 < r < 3.5 and not math.isinf(r)]
        
        if not clean:
            return 3.5 # Ako nema ničeg u sigurnom pojasu, put je čist
            
        return min(clean) # Uzmi najbliži STVARNI objekt

    def scan_callback(self, msg):
        # 1. Priprema podataka
        ranges = msg.ranges
        n = len(ranges)
        if n == 0:
            return

        # Ovdje dodajemo tvoj novi filter za 'inf' vrijednosti odmah na početku
        # Ovo osigurava da get_dist uvijek radi s brojevima
        ranges = [r if (0.1 < r < 3.5) else 3.5 for r in ranges]

        # 2. Definiranje sektora (Zadržavamo tvoju logiku indeksa)
        mid = n // 2
        s = n // 8 

        # 3. Dohvaćanje filtriranih udaljenosti pomoću tvoje get_dist metode
        dist_front = self.get_dist(ranges[mid-s : mid+s])
        dist_left = self.get_dist(ranges[mid+s : mid+3*s])
        dist_right = self.get_dist(ranges[mid-3*s : mid-s])

        # 4. Slanje podataka (NOVI FORMAT: "front:left:right")
        # Više ne šaljemo 'state' (string), nego tri broja
        msg_out = String()
        msg_out.data = f"{dist_front:.2f}:{dist_left:.2f}:{dist_right:.2f}"
        self.pub.publish(msg_out)
        
        # DEBUG LOG: Pomaže ti da vidiš što robot vidi u realnom vremenu
        self.get_logger().info(f"F:{dist_front:.2f}m | L:{dist_left:.2f}m | R:{dist_right:.2f}m")

def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Sigurno uništavanje čvora pri gašenju[cite: 1, 4]
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()