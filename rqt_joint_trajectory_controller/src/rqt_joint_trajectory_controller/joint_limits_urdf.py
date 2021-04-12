#!/usr/bin/env python

# TODO: Use urdf_parser_py.urdf instead. I gave it a try, but got
#  Exception: Required attribute not set in XML: upper
# upper is an optional attribute, so I don't understand what's going on
# See comments in https://github.com/ros/urdfdom/issues/36

import xml.dom.minidom
from math import pi

import rclpy
from rclpy.node import Node
from rcl_interfaces.srv import GetParameters

# call_get_parameters taken from ros2cli
# there does not appear to be a way yet to easily get params hosted by another node
# https://github.com/ros2/ros2cli/blob/c00dec0a72c049d3a4a8a80f1324ea24dc8373c6/ros2param/ros2param/api/__init__.py#L122
def call_get_parameters(*, node, node_name, parameter_names):
    # create client
    client = node.create_client(
        GetParameters,
        '{node_name}/get_parameters'.format_map(locals()))

    # call as soon as ready
    ready = client.wait_for_service(timeout_sec=5.0)
    if not ready:
        raise RuntimeError('Wait for service timed out')

    request = GetParameters.Request()
    request.names = parameter_names
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)

    # handle response
    response = future.result()
    if response is None:
        e = future.exception()
        raise RuntimeError(
            'Exception while calling service of node '
            "'{args.node_name}': {e}".format_map(locals()))
    return response


def get_joint_limits(n, key='robot_description', use_smallest_joint_limits=True):
    use_small = use_smallest_joint_limits
    use_mimic = True

    # Code inspired on the joint_state_publisher package by David Lu!!!
    # https://github.com/ros/robot_model/blob/indigo-devel/
    # joint_state_publisher/joint_state_publisher/joint_state_publisher
    #description = n.get_parameter(key)
    description = call_get_parameters(node=n,node_name='robot_state_publisher', parameter_names=[key]).values[0].string_value
    robot = xml.dom.minidom.parseString(description)\
        .getElementsByTagName('robot')[0]
    dependent_joints = {}
    free_joints = {}

    # Find all non-fixed joints
    for child in robot.childNodes:
        if child.nodeType is child.TEXT_NODE:
            continue
        if child.localName == 'joint':
            jtype = child.getAttribute('type')
            if jtype == 'fixed':
                continue
            name = child.getAttribute('name')
            try:
                limit = child.getElementsByTagName('limit')[0]
            except:
                continue
            if jtype == 'continuous':
                minval = -pi
                maxval = pi
            else:
                try:
                    minval = float(limit.getAttribute('lower'))
                    maxval = float(limit.getAttribute('upper'))
                except:
                    continue
            try:
                maxvel = float(limit.getAttribute('velocity'))
            except:
                continue
            safety_tags = child.getElementsByTagName('safety_controller')
            if use_small and len(safety_tags) == 1:
                tag = safety_tags[0]
                if tag.hasAttribute('soft_lower_limit'):
                    minval = max(minval,
                                 float(tag.getAttribute('soft_lower_limit')))
                if tag.hasAttribute('soft_upper_limit'):
                    maxval = min(maxval,
                                 float(tag.getAttribute('soft_upper_limit')))

            mimic_tags = child.getElementsByTagName('mimic')
            if use_mimic and len(mimic_tags) == 1:
                tag = mimic_tags[0]
                entry = {'parent': tag.getAttribute('joint')}
                if tag.hasAttribute('multiplier'):
                    entry['factor'] = float(tag.getAttribute('multiplier'))
                if tag.hasAttribute('offset'):
                    entry['offset'] = float(tag.getAttribute('offset'))

                dependent_joints[name] = entry
                continue

            if name in dependent_joints:
                continue

            joint = {'min_position': minval, 'max_position': maxval}
            joint["has_position_limits"] = jtype != 'continuous'
            joint['max_velocity'] = maxvel
            free_joints[name] = joint
    return free_joints
