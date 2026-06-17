import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class DriveForward(Node):
    def __init__(self):
        super().__init__('drive_forward')
        # TODO: create a publisher of Twist on '/cmd_vel', queue 10
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        # TODO: create a timer (e.g. 0.1s) calling self.timer_callback
        self.timer = self.create_timer(0.1, self.timer_callback)
        # TODO: record the start time — self.start_time = self.get_clock().now()
        self.start_time = self.get_clock().now()

    def timer_callback(self):
        # TODO: compute how long the node has been running
        elapsed_time = (self.get_clock().now() - self.start_time).nanoseconds / 1e9  # convert to seconds
        # TODO: if under N seconds -> publish a Twist with linear.x = 0.2
        if elapsed_time < 6.28:     # move semi circle for 5 seconds
            msg = Twist()
            msg.linear.x = 0.5
            msg.angular.z = 0.5
            self.publisher_.publish(msg)
        elif elapsed_time < 12.56:  # move semi circle for 5 seconds
            msg = Twist()
            msg.linear.x = 0.5
            msg.angular.z = -0.5
            self.publisher_.publish(msg)
        elif elapsed_time < 18.84:   # move semi circle for 5 seconds
            msg = Twist()
            msg.linear.x = 0.5
            msg.angular.z = -0.5
            self.publisher_.publish(msg)
        elif elapsed_time < 25.12:   # move semi circle for 5 seconds
            msg = Twist()
            msg.linear.x = 0.5
            msg.angular.z = 0.5
            self.publisher_.publish(msg)
        elif elapsed_time < 31.4:  # stop
            msg = Twist()
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.publisher_.publish(msg)



def main(args=None):
    rclpy.init(args=args)
    node = DriveForward()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()