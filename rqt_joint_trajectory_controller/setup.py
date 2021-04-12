from setuptools import setup

package_name = 'rqt_joint_trajectory_controller'
setup(
    name=package_name,
    version='1.0.0',
    package_dir={'': 'src'},
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
        ('share/' + package_name + '/resource', [
        'resource/joint_trajectory_controller.ui',
        'resource/double_editor.ui',
        'resource/off.svg',
        'resource/on.svg',
        'resource/scope.png',
        'resource/scope.svg'
        ]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['plugin.xml'])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Dirk Thomas',
    maintainer='Dirk Thomas',
    maintainer_email='dthomas@osrfoundation.org',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description=(
        'Graphical frontend for interacting with joint_trajectory_controller instances.'
    ),
    license='BSD',
    entry_points = {
        'console_scripts': [
            'rqt_joint_trajectory_controller = rqt_joint_trajectory_controller.joint_trajectory_controller:main'
        ]
    }
)


