import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/jeagerboob/ros2_ws/install/ugv_obstacle_avoidance'
