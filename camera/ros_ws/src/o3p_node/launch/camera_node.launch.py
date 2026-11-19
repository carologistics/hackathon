from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    serial_no = LaunchConfiguration('serial_no')
    camera_name = LaunchConfiguration('camera_name')
    recording = LaunchConfiguration('recording')
    loop = LaunchConfiguration('loop')
    use_timestamps = LaunchConfiguration('use_timestamps')
    publish_map_transform = LaunchConfiguration('publish_map_transform')
    enable_pointcloud = LaunchConfiguration('enable_pointcloud')
    enable_depth = LaunchConfiguration('enable_depth')
    enable_ir = LaunchConfiguration('enable_ir')
    enable_rgb = LaunchConfiguration('enable_rgb')
    enable_imu = LaunchConfiguration('enable_imu')
    launch_prefix = LaunchConfiguration('launch_prefix')

    return LaunchDescription([
        DeclareLaunchArgument(
            'serial_no',
            default_value='',
            description='Serial number of the camera to open. Empty selects the first available camera.',
        ),
        DeclareLaunchArgument(
            'camera_name',
            default_value='camera',
            description='Name used as prefix for topics and TF frames so several cameras can be distinguished.',
        ),
        DeclareLaunchArgument(
            'recording',
            default_value='',
            description='Path to a recording (.bag) to play back instead of opening a live camera. '
                        'Empty uses a live camera.',
        ),
        DeclareLaunchArgument(
            'loop',
            default_value='true',
            description='Whether to loop the playback once the end of the recording is reached.',
        ),
        DeclareLaunchArgument(
            'use_timestamps',
            default_value='true',
            description='Whether to delay frame delivery according to the recorded timestamps.',
        ),
        DeclareLaunchArgument(
            'publish_map_transform',
            default_value='false',
            description='Publish the convenience "map" -> camera root transform. Off by default; '
                        'enable it for the stand-alone rviz "map" fixed-frame setup.',
        ),
        DeclareLaunchArgument(
            'enable_pointcloud',
            default_value='true',
            description='Compute and publish the point cloud topics.',
        ),
        DeclareLaunchArgument(
            'enable_depth',
            default_value='true',
            description='Compute and publish the depth topics.',
        ),
        DeclareLaunchArgument(
            'enable_ir',
            default_value='true',
            description='Compute and publish the IR topic.',
        ),
        DeclareLaunchArgument(
            'enable_rgb',
            default_value='true',
            description='Compute and publish the RGB topic.',
        ),
        DeclareLaunchArgument(
            'enable_imu',
            default_value='true',
            description='Publish the IMU topics.',
        ),
        DeclareLaunchArgument(
            'launch_prefix',
            default_value='',
            description='Optional command prefix to wrap the node, e.g. '
                        "'gdb -batch -ex run -ex bt --args' or 'valgrind'. Empty by default.",
        ),
        Node(
            package='o3p_node',
            executable='camera_node',
            name='o3p_camera',
            output='screen',
            prefix=launch_prefix,
            parameters=[{
                'serial_no': serial_no,
                'camera_name': camera_name,
                'recording': recording,
                'loop': loop,
                'use_timestamps': use_timestamps,
                'publish_map_transform': publish_map_transform,
                'enable_pointcloud': enable_pointcloud,
                'enable_depth': enable_depth,
                'enable_ir': enable_ir,
                'enable_rgb': enable_rgb,
                'enable_imu': enable_imu,
            }],
        ),
    ])
