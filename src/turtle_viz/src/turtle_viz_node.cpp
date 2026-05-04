#include <rclcpp/rclcpp.hpp>
#include <turtlesim/msg/pose.hpp>
#include <nav_msgs/msg/path.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <visualization_msgs/msg/marker.hpp>
#include <tf2_ros/transform_broadcaster.h>
#include <tf2/LinearMath/Quaternion.h>

class TurtleViz : public rclcpp::Node
{
public:
  TurtleViz() : Node("turtle_viz")
  {
    pose_sub_ = create_subscription<turtlesim::msg::Pose>(
      "/turtle1/pose", 10,
      std::bind(&TurtleViz::on_pose, this, std::placeholders::_1));

    path_pub_   = create_publisher<nav_msgs::msg::Path>("/turtle1/path", 10);
    marker_pub_ = create_publisher<visualization_msgs::msg::Marker>("/turtle1/marker", 10);
    tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);

    path_.header.frame_id = "world";
  }

private:
  void on_pose(const turtlesim::msg::Pose::SharedPtr msg)
  {
    const auto now = get_clock()->now();

    tf2::Quaternion q;
    q.setRPY(0.0, 0.0, msg->theta);

    // broadcast TF: world -> turtle1
    geometry_msgs::msg::TransformStamped tf;
    tf.header.stamp    = now;
    tf.header.frame_id = "world";
    tf.child_frame_id  = "turtle1";
    tf.transform.translation.x = msg->x;
    tf.transform.translation.y = msg->y;
    tf.transform.rotation.x = q.x();
    tf.transform.rotation.y = q.y();
    tf.transform.rotation.z = q.z();
    tf.transform.rotation.w = q.w();
    tf_broadcaster_->sendTransform(tf);

    // append to trail
    geometry_msgs::msg::PoseStamped ps;
    ps.header.stamp    = now;
    ps.header.frame_id = "world";
    ps.pose.position.x = msg->x;
    ps.pose.position.y = msg->y;
    ps.pose.orientation.x = q.x();
    ps.pose.orientation.y = q.y();
    ps.pose.orientation.z = q.z();
    ps.pose.orientation.w = q.w();
    path_.header.stamp = now;
    path_.poses.push_back(ps);
    path_pub_->publish(path_);

    // arrow marker at current pose
    visualization_msgs::msg::Marker marker;
    marker.header      = ps.header;
    marker.ns          = "turtle";
    marker.id          = 0;
    marker.type        = visualization_msgs::msg::Marker::ARROW;
    marker.action      = visualization_msgs::msg::Marker::ADD;
    marker.pose        = ps.pose;
    marker.scale.x     = 0.5;
    marker.scale.y     = 0.1;
    marker.scale.z     = 0.1;
    marker.color.r     = 0.2f;
    marker.color.g     = 0.8f;
    marker.color.b     = 0.2f;
    marker.color.a     = 1.0f;
    marker_pub_->publish(marker);
  }

  rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr pose_sub_;
  rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr path_pub_;
  rclcpp::Publisher<visualization_msgs::msg::Marker>::SharedPtr marker_pub_;
  std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
  nav_msgs::msg::Path path_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<TurtleViz>());
  rclcpp::shutdown();
  return 0;
}
