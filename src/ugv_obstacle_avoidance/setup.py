import os
import glob
from setuptools import find_packages, setup

package_name = 'ugv_obstacle_avoidance'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Launch files
        (os.path.join('share', package_name, 'launch'),
            glob.glob('launch/*.py')),
        # World files
        (os.path.join('share', package_name, 'worlds'),
            glob.glob('worlds/*.world')),
        # URDF files
        (os.path.join('share', package_name, 'urdf'),
            glob.glob('urdf/*.urdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jeagerboob',
    maintainer_email='jeagerboob@todo.todo',
    description='UGV obstacle avoidance using reactive FSM and simulated LiDAR in Gazebo',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'obstacle_avoidance_node = ugv_obstacle_avoidance.obstacle_avoidance_node:main',
        ],
    },
)
