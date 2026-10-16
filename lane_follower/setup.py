from setuptools import find_packages, setup

packageName = 'lane_follower'

setup(
    name=packageName,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + packageName]),
        ('share/' + packageName, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Saivya Kishore',
    maintainer_email='saivya.kishore@gmail.com',
    description='Camera-based yellow and white lane follower for ROS 2',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'follower_node = lane_follower.follower_node:main',
        ],
    },
)
