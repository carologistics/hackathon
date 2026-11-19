import os
import sys

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# USB vendor/product IDs for o3p cameras (mirrors UsbCommon.hpp).
_O3P_USB_VID = '1c28'
_O3P_USB_PID = 'f003'


def _discover_serials():
    """Return sorted list of o3p camera serial numbers via sysfs (Linux only).

    Iterate /sys/bus/usb/devices,
    match idVendor/idProduct, read the serial attribute.
    """
    serials = set()
    base = '/sys/bus/usb/devices'
    try:
        for name in os.listdir(base):
            dev = os.path.join(base, name)
            try:
                vid = open(os.path.join(dev, 'idVendor')).read().strip().lower()
                pid = open(os.path.join(dev, 'idProduct')).read().strip().lower()
                if vid == _O3P_USB_VID and pid == _O3P_USB_PID:
                    serial_path = os.path.join(dev, 'serial')
                    if os.path.exists(serial_path):
                        serials.add(open(serial_path).read().strip())
            except OSError:
                continue
    except OSError as exc:
        print('[multi_camera.launch.py] Could not read {}: {}'.format(base, exc),
              file=sys.stderr)
    return sorted(serials)


def launch_setup(context, *args, **kwargs):
    # Comma separated list of serial numbers, one per camera to open.
    serials = [s.strip() for s in LaunchConfiguration('serial_nos').perform(context).split(',') if s.strip()]
    # Optional comma separated list of names. Falls back to camera1, camera2, ...
    names = [n.strip() for n in LaunchConfiguration('camera_names').perform(context).split(',') if n.strip()]

    # Optional debugger/profiler wrapper (e.g. 'gdb -batch -ex run -ex bt --args').
    # Empty by default so normal launches are unaffected.
    launch_prefix = LaunchConfiguration('launch_prefix').perform(context).strip()

    # Shared options applied to every camera node. Parse the booleans once here so the
    # same value is forwarded to each node (the strings come from the launch arguments).
    def _as_bool(name):
        return LaunchConfiguration(name).perform(context).strip().lower() in ('1', 'true', 'yes', 'on')

    shared_params = {
        'publish_map_transform': _as_bool('publish_map_transform'),
        'enable_pointcloud': _as_bool('enable_pointcloud'),
        'enable_depth': _as_bool('enable_depth'),
        'enable_ir': _as_bool('enable_ir'),
        'enable_rgb': _as_bool('enable_rgb'),
        'enable_imu': _as_bool('enable_imu'),
    }

    if not serials:
        serials = _discover_serials()
        if not serials:
            print('[multi_camera.launch.py] No o3p cameras found; no nodes will be launched.',
                  file=sys.stderr)

    nodes = []
    for index, serial in enumerate(serials):
        camera_name = names[index] if index < len(names) else 'camera{}'.format(index + 1)
        node_kwargs = dict(
            package='o3p_node',
            executable='camera_node',
            name='o3p_camera_{}'.format(index + 1),
            output='screen',
            parameters=[{
                'serial_no': serial,
                'camera_name': camera_name,
                **shared_params,
            }],
        )
        if launch_prefix:
            node_kwargs['prefix'] = launch_prefix
        nodes.append(Node(**node_kwargs))
    return nodes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'serial_nos',
            default_value='',
            description='Comma separated list of camera serial numbers to open, one node per serial. '
                        'When empty, all connected cameras are opened automatically.',
        ),
        DeclareLaunchArgument(
            'camera_names',
            default_value='',
            description='Optional comma separated list of names used as topic/TF prefixes. '
                        'Defaults to camera1, camera2, ... when omitted.',
        ),
        DeclareLaunchArgument(
            'publish_map_transform',
            default_value='false',
            description='Publish the convenience "map" -> camera root transform for every camera. '
                        'Off by default; enable it for the stand-alone rviz "map" fixed-frame setup.',
        ),
        DeclareLaunchArgument(
            'enable_pointcloud',
            default_value='true',
            description='Compute and publish the point cloud topics on every camera.',
        ),
        DeclareLaunchArgument(
            'enable_depth',
            default_value='true',
            description='Compute and publish the depth topics on every camera.',
        ),
        DeclareLaunchArgument(
            'enable_ir',
            default_value='true',
            description='Compute and publish the IR topic on every camera.',
        ),
        DeclareLaunchArgument(
            'enable_rgb',
            default_value='true',
            description='Compute and publish the RGB topic on every camera.',
        ),
        DeclareLaunchArgument(
            'enable_imu',
            default_value='true',
            description='Publish the IMU topics on every camera.',
        ),
        DeclareLaunchArgument(
            'launch_prefix',
            default_value='',
            description='Optional command prefix to wrap each node, e.g. '
                        "'gdb -batch -ex run -ex bt --args' or 'valgrind'. Empty by default.",
        ),
        OpaqueFunction(function=launch_setup),
    ])
