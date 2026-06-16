import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TalkerNode(Node):
    def __init__(self):
        super().__init__('talker')          # registers the node name with ROS
        # TODO: create a publisher
        # TODO: create a timer that calls self.timer_callback every 1.0s
        # TODO: a counter variable for the message text

    def timer_callback(self):
        # TODO: build a String message
        # TODO: set its .data field to some text (include the counter)
        # TODO: publish it
        # TODO: log it so you see it in the terminal
        pass


def main(args=None):
    rclpy.init(args=args)
    node = TalkerNode()
    rclpy.spin(node)            # keeps the node alive, firing timers/callbacks
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()