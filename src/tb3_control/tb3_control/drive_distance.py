import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from math import sqrt


class DriveDistance(Node):
    def __init__(self):
        super().__init__('drive_distance')
        # TODO: create a publisher of Twist on '/cmd_vel', queue 10
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        # TODO: create a subscription to Odometry on '/odom', callback self.odom_callback, queue 10
        self.subscription = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        # TODO: set self.target_distance = 1.0  (metres)
        self.target_distance = 1.0
        # TODO: self.start_x = None  and  self.start_y = None  (we don't know start yet)
        self.start_x = None
        self.start_y = None

    def odom_callback(self, msg):
        # Extract current position from the odometry message
        current_x = msg.pose.pose.position.x
        current_y = msg.pose.pose.position.y

        # TODO: on the FIRST callback, record start_x/start_y (they're still None)
        #       then return (nothing to do yet)
        if self.start_x is None and self.start_y is None:
            self.start_x = current_x
            self.start_y = current_y
            self.get_logger().info(f'Start position recorded: ({self.start_x}, {self.start_y})')
            return

        # TODO: compute distance travelled from start using sqrt((cx-sx)^2 + (cy-sy)^2)
        distance = sqrt((current_x - self.start_x) ** 2 + (current_y - self.start_y) ** 2)

        # TODO: build a Twist
        #       if distance < target -> linear.x = 0.2 (keep going)
        #       else                 -> linear.x = 0.0 (stop)
        #       publish it
        twist = Twist()
        if distance < self.target_distance:
            twist.linear.x = 0.2
            # self.get_logger().info(f'Distance travelled: {distance:.2f} m, moving forward.')
        else:
            twist.linear.x = 0.0
            self.get_logger().info(f'Distance travelled: {distance:.2f} m, target reached. Stopping.')
        
        self.publisher.publish(twist)



def main(args=None):
    rclpy.init(args=args)
    node = DriveDistance()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()