import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
import collections
import numpy as np
class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')
        self.sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.pub = self.create_publisher(String, '/perception_state', 10)
        self.buf_f = collections.deque([5.0]*8, maxlen=8)
        self.buf_l = collections.deque([5.0]*8, maxlen=8)
        self.buf_r = collections.deque([5.0]*8, maxlen=8)
                # Memorija za stabilizaciju (da ne titra)
        self.last_distances = {"F": 5.0, "L": 5.0, "R": 5.0}

    def clean_sector(self, ranges, key):
        # 1. Izbaci sve nule, inf i samoočitavanja (ispod 0.3m)
        valid = [r for r in ranges if 0.3 < r < 4.8]
        
        if valid:
            # Uzmi minimalnu udaljenost, to je najsigurnije
            current_min = min(valid)
            self.last_distances[key] = current_min
            return current_min
        else:
            # Ako senzor trenutno "fali" (izbaci 5m), a zid je bio blizu
            # zadrži zadnju poznatu vrijednost (to je "prevara" koja spašava stvar)
            if self.last_distances[key] < 1.5:
                return self.last_distances[key]
            return 5.0

    def scan_callback(self, msg):
        n = len(msg.ranges)
        mid = n // 2
        
        # Širina vidnog polja (cca 15-20 stupnjeva po sektoru)
        width = n // 12 

        # --- DEFINICIJA SEKTORA (Prilagođeno tvom robotu) ---
        # Ako su ti 'krajevi' liste (0 i n) naprijed, koristimo ovo:
        f_raw = msg.ranges[-width:] + msg.ranges[:width]
        
        # Desno je isječak oko 1/4 liste (ako 0-n pokriva 360 stupnjeva)
        # ili oko n//4 ako pokriva 180. Prilagodi prema potrebi:
        r_raw = msg.ranges[int(n*0.2) : int(n*0.3)]
        
        # Lijevo je suprotna strana
        l_raw = msg.ranges[int(n*0.7) : int(n*0.8)]

        def process_sector(raw_data, buffer):
            # 1. Filtriraj smeće (ispod 0.3m je robot, iznad 5m je beskonačno)
            valid = [r for r in raw_data if 0.3 < r < 4.9]
            
            if valid:
                # Uzmi 10. percentil (pouzdanije od čistog minimuma koji može biti šum)
                current_min = np.percentile(valid, 10)
            else:
                current_min = 5.0
                
            buffer.append(current_min)
            # 2. Vrati medijan buffera (ekstremno otporno na 'skakanje' podataka)
            return float(np.median(buffer))

        f_dist = process_sector(f_raw, self.buf_f)
        l_dist = process_sector(l_raw, self.buf_l)
        r_dist = process_sector(r_raw, self.buf_r)

        msg_out = String()
        msg_out.data = f"{f_dist:.2f}:{l_dist:.2f}:{r_dist:.2f}"
        self.pub.publish(msg_out)

        self.get_logger().info(f"ZID -> NAPRIJED: {f_dist:.2f}m | DESNO: {r_dist:.2f}m | LIJEVO: {l_dist:.2f}m")

def main():
    rclpy.init()
    node = PerceptionNode()
    rclpy.spin(node)
    rclpy.shutdown()