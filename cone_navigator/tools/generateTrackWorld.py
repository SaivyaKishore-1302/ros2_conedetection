import math
from pathlib import Path


orangePoints = [
    (0.000, 0.350),
    (1.966, 0.348),
    (3.884, 0.730),
    (5.791, 1.681),
    (7.187, 3.157),
    (7.456, 4.936),
    (6.576, 6.531),
    (4.800, 7.150),
    (2.994, 6.509),
    (1.778, 5.088),
    (0.737, 3.542),
    (-0.952, 2.653),
    (-2.946, 2.954),
    (-4.539, 2.167),
    (-5.150, 0.500),
    (-4.531, -1.276),
    (-3.165, -2.191),
    (-2.224, 0.269),
]

bluePoints = [
    (0.000, -0.350),
    (2.034, -0.348),
    (4.116, 0.070),
    (6.209, 1.119),
    (7.813, 2.843),
    (8.144, 5.064),
    (7.024, 7.069),
    (4.800, 7.850),
    (2.606, 7.091),
    (1.222, 5.512),
    (0.263, 4.058),
    (-1.048, 3.347),
    (-3.054, 3.646),
    (-5.061, 2.633),
    (-5.850, 0.500),
    (-5.069, -1.724),
    (-2.835, -2.809),
    (-1.776, -0.269),
]


def densify(points, maxSpacing):
    densePoints = []
    for index, start in enumerate(points):
        end = points[(index + 1) % len(points)]
        distance = math.hypot(end[0] - start[0], end[1] - start[1])
        divisions = max(1, math.ceil(distance / maxSpacing))
        for step in range(divisions):
            ratio = step / divisions
            x = start[0] + ratio * (end[0] - start[0])
            y = start[1] + ratio * (end[1] - start[1])
            densePoints.append((x, y))
    return densePoints


def boundaryModel(name, points, colour):
    lines = [
        f'    <model name="{name}">',
        '      <static>true</static>',
        '      <link name="link">',
    ]
    for index, point in enumerate(points):
        collisionPose = f'{point[0]:.3f} {point[1]:.3f} 0.05 0 0 0'
        visualPose = f'{point[0]:.3f} {point[1]:.3f} 0.2 0 0 0'
        lines.extend([
            f'        <collision name="collision_{index}">',
            f'          <pose>{collisionPose}</pose>',
            '          <geometry>',
            '            <cylinder><radius>0.06</radius><length>0.1</length></cylinder>',
            '          </geometry>',
            '        </collision>',
            f'        <visual name="visual_{index}">',
            f'          <pose>{visualPose}</pose>',
            '          <geometry>',
            '            <cylinder><radius>0.12</radius><length>0.4</length></cylinder>',
            '          </geometry>',
            '          <material>',
            f'            <ambient>{colour}</ambient>',
            f'            <diffuse>{colour}</diffuse>',
            '            <specular>0.1 0.1 0.1 1</specular>',
            '          </material>',
            '        </visual>',
        ])
    lines.extend([
        '      </link>',
        '    </model>',
    ])
    return lines


def main():
    orange = densify(orangePoints, 0.25)
    blue = densify(bluePoints, 0.25)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<sdf version="1.6">',
        '  <world name="cone_track">',
        '    <include>',
        '      <uri>model://ground_plane</uri>',
        '    </include>',
        '    <include>',
        '      <uri>model://sun</uri>',
        '    </include>',
        '    <physics type="ode">',
        '      <max_step_size>0.001</max_step_size>',
        '      <real_time_factor>1</real_time_factor>',
        '    </physics>',
    ]
    lines.extend(boundaryModel('orange_boundary', orange, '1.0 0.3 0.0 1'))
    lines.extend(boundaryModel('blue_boundary', blue, '0.0 0.2 1.0 1'))
    lines.extend([
        '  </world>',
        '</sdf>',
    ])
    outputPath = Path(__file__).resolve().parents[1] / 'worlds' / 'track_world.sdf'
    outputPath.write_text('\n'.join(lines) + '\n')
    print(f'orange={len(orange)} blue={len(blue)}')


if __name__ == '__main__':
    main()
