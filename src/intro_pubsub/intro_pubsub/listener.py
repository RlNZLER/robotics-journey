import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ListenerNode(Node):
    def __init__(self):
        super().__init__('listener')
        # TODO: create a subscription
        self.subscriber_ = self.create_subscription(String, 'chatter', self.listener_callback, 10)  # topic name is 'chatter', queue size is 10
        # TODO: (no timer needed — subscribers are event-driven)

    def listener_callback(self, msg):
        # TODO: log the received message's data
        self.get_logger().info(f'I heard: "{msg.data}"')
        pass


def main(args=None):
    rclpy.init(args=args)
    node = ListenerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()