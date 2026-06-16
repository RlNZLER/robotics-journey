import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TalkerNode(Node):
    def __init__(self):
        super().__init__('talker')          # registers the node name with ROS
        # TODO: create a publisher
        self.publisher_ = self.create_publisher(String, 'chatter', 10)  # topic name is 'chatter', queue size is 10
        # TODO: create a timer that calls self.timer_callback every 1.0s
        self.create_timer(1.0, self.timer_callback)  # timer period is 1.0 seconds
        # TODO: a counter variable for the message text
        self.counter = 0

    def timer_callback(self):
        # TODO: build a String message
        msg = String()
        # TODO: set its .data field to some text (include the counter)
        msg.data = f'Hello, world! {self.counter}'
        # TODO: publish it
        self.publisher_.publish(msg)
        # TODO: log it so you see it in the terminal
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.counter += 1


def main(args=None):
    rclpy.init(args=args)
    node = TalkerNode()
    rclpy.spin(node)            # keeps the node alive, firing timers/callbacks
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()