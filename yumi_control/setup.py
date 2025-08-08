from setuptools import setup
from glob import glob
import os

package_name = 'yumi_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', [f'resource/{package_name}']),
        (f'share/{package_name}', ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ernests Petersons',
    maintainer_email='erpeetersons2002@gmail.com',
    description='YuMi dual-arm control package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'move_to_xyz = yumi_control.move_to_xyz:main',
            'kinect2_pointcloud = yumi_control.kinect2_pointcloud:main',
        ],
    },
)
