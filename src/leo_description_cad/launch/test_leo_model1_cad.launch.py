"""
Standalone sanity-check launch file for leo_model1_cad.urdf.xacro.

v4: mirrors the structure of the project's known-working leo_gz.launch.py
as closely as possible -- same GPU-offload env vars, same
IncludeLaunchDescription(gz_sim.launch.py) pattern, and critically:
points gz_args at a real world file by full path (leo_gz_worlds'
leo_empty.sdf) instead of the bare string 'empty.sdf', which may not
have been resolving to any actual file.
"""
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration, Command
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_leo_gz_worlds = get_package_share_directory('leo_gz_worlds')
    world_path = os.path.join(pkg_leo_gz_worlds, 'worlds', 'leo_empty.sdf')

    # Same GPU-offload vars as leo_gz.launch.py -- proven to work in this
    # exact launch pattern on this machine.
    gpu_offload_1 = SetEnvironmentVariable('__NV_PRIME_RENDER_OFFLOAD', '1')
    gpu_offload_2 = SetEnvironmentVariable('__GLX_VENDOR_LIBRARY_NAME', 'nvidia')
    gpu_offload_3 = SetEnvironmentVariable('__VK_LAYER_NV_optimus', 'NVIDIA_only')

    # Our package's mesh resource path, additive to whatever's already set.
    set_resource_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '') + ':' +
              os.path.join(get_package_share_directory('leo_description_cad'), '..')
    )
    set_qt_platform = SetEnvironmentVariable(name='QT_QPA_PLATFORM', value='xcb')

    xacro_path_arg = DeclareLaunchArgument(
        'xacro_path',
        default_value=os.path.join(
            get_package_share_directory('leo_description_cad'),
            'urdf', 'leo_model1_cad.urdf.xacro'
        ),
        description='Path to leo_model1_cad.urdf.xacro'
    )

    robot_description = ParameterValue(
        Command(['xacro ', LaunchConfiguration('xacro_path')]),
        value_type=str
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
    )

    # Real, known-good world file by full path -- mirrors sim_world in
    # leo_gz.launch.py, instead of the bare 'empty.sdf' string.
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': world_path}.items(),
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'leo_model1_cad',
            '-z', '0.3',
        ],
        output='screen',
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen',
    )

    return LaunchDescription([
        gpu_offload_1,
        gpu_offload_2,
        gpu_offload_3,
        set_resource_path,
        set_qt_platform,
        xacro_path_arg,
        robot_state_publisher,
        gz_sim,
        spawn,
        clock_bridge,
    ])
