
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from ugv_obstacle_avoidance.state_machine import ObstacleAvoidanceFSM, State
VEL_MOVING_LINEAR    =  0.3
VEL_AVOIDING_LINEAR  =  0.15
VEL_TURNING_LINEAR   =  0.0
VEL_STOPPED_LINEAR   =  0.0
VEL_RECOVERING_LINEAR = -0.2

VEL_AVOID_ANGULAR    =  0.6
VEL_TURNING_ANGULAR  =  0.6
SECTOR_HALF = 30  # degrees


class ObstacleAvoidanceNode(Node):

    def __init__(self):
        super().__init__('obstacle_avoidance_node')
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
        )
        self._cmd_pub   = self.create_publisher(Twist,  '/cmd_vel',     10)
        self._state_pub = self.create_publisher(String, '/robot_state', 10)
        self._scan_sub = self.create_subscription(
            LaserScan, '/scan', self._scan_cb, sensor_qos)
        self._fsm = ObstacleAvoidanceFSM(
            logger_fn=lambda msg: self.get_logger().info(msg))
        self._fsm.start()
        self._log_timer = self.create_timer(1.0, self._log_status)
        self._last_sectors = {'front': float('inf'),
                              'left':  float('inf'),
                              'right': float('inf'),
                              'rear':  float('inf')}

        self.get_logger().info('ObstacleAvoidanceNode started.')

    def _scan_cb(self, msg: LaserScan):
        sectors = self._split_sectors(msg)
        self._last_sectors = sectors

        # Advance FSM
        self._fsm.update(
            front=sectors['front'],
            left=sectors['left'],
            right=sectors['right'],
            rear=sectors['rear'],
        )
        twist = self._state_to_twist(self._fsm.state, sectors)
        self._cmd_pub.publish(twist)
        state_msg = String()
        state_msg.data = self._fsm.state.name
        self._state_pub.publish(state_msg)

    def _split_sectors(self, msg: LaserScan) -> dict:
        ranges = list(msg.ranges)
        n = len(ranges)

        def safe_range(r, max_r):
            if math.isnan(r) or math.isinf(r) or r <= 0.0:
                return max_r
            return r

        safe = [safe_range(r, msg.range_max) for r in ranges]

        def angle_to_idx(angle_deg):
            angle_rad = math.radians(angle_deg)
            idx = int(round(
                (angle_rad - msg.angle_min) / msg.angle_increment
            ))
            return idx % n

        def sector_min(centre_deg, half_deg):
            indices = []
            for d in range(-half_deg, half_deg + 1):
                indices.append(angle_to_idx(centre_deg + d))
            return min(safe[i] for i in indices)

        return {
            'front': sector_min(0,   SECTOR_HALF),
            'left':  sector_min(90,  SECTOR_HALF),
            'rear':  sector_min(180, SECTOR_HALF),
            'right': sector_min(270, SECTOR_HALF),
        }

    def _state_to_twist(self, state: State, sectors: dict) -> Twist:
        twist = Twist()
        d = self._fsm.turn_direction  # +1 = left, -1 = right

        if state == State.IDLE:
            pass

        elif state == State.MOVING:
            twist.linear.x  = VEL_MOVING_LINEAR
            twist.angular.z = 0.0

        elif state == State.AVOIDING:
            twist.linear.x  = VEL_AVOIDING_LINEAR
            twist.angular.z = d * VEL_AVOID_ANGULAR

        elif state == State.TURNING:
            twist.linear.x  = VEL_TURNING_LINEAR
            twist.angular.z = d * VEL_TURNING_ANGULAR

        elif state == State.STOPPED:
            twist.linear.x  = VEL_STOPPED_LINEAR
            twist.angular.z = 0.0

        elif state == State.RECOVERING:
            twist.linear.x  = VEL_RECOVERING_LINEAR
            twist.angular.z = 0.0

        return twist
    def _log_status(self):
        s = self._last_sectors
        self.get_logger().info(
            f"State: {self._fsm.state.name:<10} | "
            f"F:{s['front']:5.2f}  L:{s['left']:5.2f}  "
            f"R:{s['right']:5.2f}  Rear:{s['rear']:5.2f}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidanceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
