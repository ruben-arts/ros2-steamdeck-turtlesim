"""
Teleop node for controlling turtlesim with a Steam Deck gamepad or keyboard.

Joystick  : left stick Y -> linear.x  |  left stick X -> angular.z
Keyboard  : arrow up/down -> linear.x  |  arrow left/right -> angular.z

Run turtlesim first:  pixi run turtlesim
Then in another terminal: pixi run teleop
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import pygame

# SDL2 axis indices for left stick
AXIS_LINEAR = 1   # Y axis (up = negative on most controllers)
AXIS_ANGULAR = 0  # X axis

MAX_LINEAR = 2.0   # m/s
MAX_ANGULAR = 2.0  # rad/s
DEADZONE = 0.08

WINDOW_SIZE = (300, 120)


def apply_deadzone(value: float, deadzone: float) -> float:
    if abs(value) < deadzone:
        return 0.0
    sign = 1.0 if value > 0 else -1.0
    return sign * (abs(value) - deadzone) / (1.0 - deadzone)


class TeleopNode(Node):
    def __init__(self) -> None:
        super().__init__("steamdeck_teleop")
        self.pub = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.timer = self.create_timer(0.05, self.publish_twist)  # 20 Hz

        pygame.init()
        pygame.joystick.init()

        # Small window required for pygame to receive keyboard events
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Turtlesim Teleop  |  Ctrl-C to quit")
        self.font = pygame.font.SysFont("monospace", 14)

        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()
            self.get_logger().info(f"Joystick: {self.joy.get_name()}")
        else:
            self.joy = None
            self.get_logger().info("No joystick found — keyboard mode")

        self.get_logger().info("Arrow keys or left stick to move  |  Ctrl-C to quit")

    def _joystick_axes(self) -> tuple[float, float]:
        raw_linear = -self.joy.get_axis(AXIS_LINEAR)
        raw_angular = -self.joy.get_axis(AXIS_ANGULAR)
        linear = apply_deadzone(raw_linear, DEADZONE) * MAX_LINEAR
        angular = apply_deadzone(raw_angular, DEADZONE) * MAX_ANGULAR
        return linear, angular

    def _keyboard_axes(self) -> tuple[float, float]:
        keys = pygame.key.get_pressed()
        linear = 0.0
        angular = 0.0
        if keys[pygame.K_UP]:
            linear = MAX_LINEAR
        elif keys[pygame.K_DOWN]:
            linear = -MAX_LINEAR
        if keys[pygame.K_LEFT]:
            angular = MAX_ANGULAR
        elif keys[pygame.K_RIGHT]:
            angular = -MAX_ANGULAR
        return linear, angular

    def publish_twist(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt

        if self.joy is not None:
            linear, angular = self._joystick_axes()
        else:
            linear, angular = self._keyboard_axes()

        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        self.pub.publish(msg)

        self._draw_hud(linear, angular)

    def _draw_hud(self, linear: float, angular: float) -> None:
        self.screen.fill((30, 30, 30))
        mode = "joystick" if self.joy else "keyboard"
        lines = [
            f"mode    : {mode}",
            f"linear  : {linear:+.2f} m/s",
            f"angular : {angular:+.2f} rad/s",
        ]
        for i, text in enumerate(lines):
            surf = self.font.render(text, True, (200, 200, 200))
            self.screen.blit(surf, (12, 12 + i * 22))
        pygame.display.flip()

    def destroy_node(self) -> None:
        pygame.quit()
        super().destroy_node()


def main() -> None:
    rclpy.init()
    node = TeleopNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
