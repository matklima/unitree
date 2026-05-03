import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
import collections
import numpy as np


class PerceptionNode(Node):

    def __init__(self):
        super().__init__('perception_node')

        self.sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10
        )
        self.pub = self.create_publisher(String, '/perception_state', 10)

        self.buf_f = collections.deque([5.0] * 8, maxlen=8)
        self.buf_l = collections.deque([5.0] * 8, maxlen=8)
        self.buf_r = collections.deque([5.0] * 8, maxlen=8)

        self.SECTOR_WIDTH_DIVIDER = 12  # Divides 360° into 30° sectors
        self.LEFT_START = 0.22
        self.LEFT_END = 0.32
        self.RIGHT_START = 0.7
        self.RIGHT_END = 0.8

        # Sensor limits and percentile
        self.MIN_RANGE = 0.3
        self.MAX_RANGE = 4.9
        self.SAFETY_PERCENTILE = 10
        self.DEFAULT_DIST = 5.0

    def scan_callback(self, msg):
        ranges = msg.ranges
        n = len(ranges)
        width = n // self.SECTOR_WIDTH_DIVIDER

        # Sectors
        f_raw = ranges[-width:] + ranges[:width]
        l_raw = ranges[int(n * self.LEFT_START): int(n * self.LEFT_END)]
        r_raw = ranges[int(n * self.RIGHT_START): int(n * self.RIGHT_END)]

        f_dist = self.process_sector(f_raw, self.buf_f)
        l_dist = self.process_sector(l_raw, self.buf_l)
        r_dist = self.process_sector(r_raw, self.buf_r)

        out = String()
        out.data = f"{f_dist:.2f}:{l_dist:.2f}:{r_dist:.2f}"
        self.pub.publish(out)

        self.get_logger().debug(
            f"F: {f_dist:.2f} | L: {l_dist:.2f} | R: {r_dist:.2f}"
        )

    def process_sector(self, raw, buffer):
        valid = [r for r in raw if self.MIN_RANGE < r < self.MAX_RANGE]

        if valid:
            dist = np.percentile(valid, self.SAFETY_PERCENTILE)
        else:
            dist = self.DEFAULT_DIST

        buffer.append(dist)
        return float(np.median(buffer))


def main():
    rclpy.init()
    node = PerceptionNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()