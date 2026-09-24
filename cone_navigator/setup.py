import os
from glob import glob
from setuptools import find_packages, setup

pkg = 'cone_navigator'

setup(
    name=pkg,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + pkg]),
        ('share/' + pkg, ['package.xml']),
        (os.path.join('share', pkg, 'launch'),
            glob('launch/*.launch.py')),
        (os.path.join('share', pkg, 'worlds'),
            glob('worlds/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'cone_detector = cone_navigator.cone_detector:main',
            'track_planner = cone_navigator.track_planner:main',
            'velocity_controller = cone_navigator.velocity_controller:main',
        ],
    },
)
