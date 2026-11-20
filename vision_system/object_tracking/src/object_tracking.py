#!/usr/bin/env python3

import cv2
import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class ObjectTrackingNode(Node):
    WINDOW_NAME = "object_tracking_server"

    def __init__(self):
        super().__init__("object_tracking_server")
        self.window_open = False
        image_topic = self.declare_parameter("image_topic", "/camera/frame_rgb").value
        self.image_subscription = self.create_subscription(
            Image, image_topic, self.show_image, qos_profile_sensor_data
        )
        self.get_logger().info(f"Waiting for camera images on {image_topic}")

    def show_image(self, message):
        encodings = {
            "bgr8": (3, None),
            "rgb8": (3, cv2.COLOR_RGB2BGR),
            "mono8": (1, None),
            "bgra8": (4, cv2.COLOR_BGRA2BGR),
            "rgba8": (4, cv2.COLOR_RGBA2BGR),
        }
        if message.encoding not in encodings:
            self.get_logger().warning(
                f"Unsupported image encoding: {message.encoding}",
                throttle_duration_sec=5.0,
            )
            return

        channels, conversion = encodings[message.encoding]
        row_width = message.width * channels
        if (
            message.width == 0
            or message.height == 0
            or message.step < row_width
            or len(message.data) != message.height * message.step
        ):
            self.get_logger().warning("Invalid camera image", throttle_duration_sec=5.0)
            return

        rows = np.frombuffer(message.data, dtype=np.uint8).reshape(
            message.height, message.step
        )
        image = rows[:, :row_width].reshape(message.height, message.width, channels)
        if conversion is not None:
            image = cv2.cvtColor(image, conversion)
        if not self.window_open:
            cv2.namedWindow(self.WINDOW_NAME, cv2.WINDOW_NORMAL)
            self.window_open = True
        cv2.imshow(self.WINDOW_NAME, image)


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = ObjectTrackingNode()
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.03)
            if not node.window_open:
                continue
            if cv2.waitKey(1) in (27, ord("q")):
                break
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            if node.window_open:
                cv2.destroyAllWindows()
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
