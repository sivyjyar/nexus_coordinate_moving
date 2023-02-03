#!/usr/bin/env python

from __future__ import print_function

import sys
from gazebo_msgs.srv import GetModelState
import rospy

def model_position():
    rospy.wait_for_service('/gazebo/get_model_state')
    try:
        model_coordinates = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
	resp_coordinates = model_coordinates('nexus_4wd_mecanum', '')
        print('x:'+str(resp_coordinates.pose.position.x)+'  y:'+str(resp_coordinates.pose.position.y))
       # print(str(resp_coordinates.pose.orientation))
    except rospy.ServiceException as e:
        print("Service call failed: %s"%e)


if __name__ == "__main__":
    model_position()
    print("Requesting")

