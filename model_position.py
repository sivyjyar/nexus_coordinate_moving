#!/usr/bin/env python

from __future__ import print_function

import sys
import rospy

from gazebo_msgs.srv import GetModelState
from geometry_msgs.msg import Twist


class GazeboMovements():

    def __init__(self, x_user, y_user, speed):
        self.x_user = x_user
        self.y_user = y_user
        self.speed = speed
        
    def model_position(self):
        rospy.wait_for_service('/gazebo/get_model_state')
        try:
            model_coordinates = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
            resp_coordinates = model_coordinates('nexus_4wd_mecanum', '')
            print('x:' + str(resp_coordinates.pose.position.x) + '  y:' + str(resp_coordinates.pose.position.y))
            self.x_real = resp_coordinates.pose.position.x
            self.y_real = resp_coordinates.pose.position.y
        except rospy.ServiceException as e:
            print("Service call failed: %s" % e)


    def distance_between(self):

        self.x_d = self.x_user - self.x_real
        self.y_d = self.y_user - self.y_real

        self.abs_xd = abs(self.x_d)
        self.abs_yd = abs(self.y_d)
        print(str(self.x_d) + 'y' + str(self.y_d))


    def calculate_movement(self):
        #speed
        if self.abs_xd > self.abs_yd:
            self.x_speed = 1.0
            self.y_speed = self.abs_yd/self.abs_xd
        else:
            self.x_speed = self.abs_xd/self.abs_yd
            self.y_speed = 1.0

       #direction
        if self.x_user < self.x_real:
            self.x_speed *= -1
        if self.y_user < self.y_real:
            self.y_speed *= -1

    def speed_reduction(self):
        if self.abs_xd < 1 and self.abs_yd < 1:
            if self.abs_xd > self.abs_yd:
                self.speed = self.abs_xd
            else:
                self.speed = self.abs_yd


    def movements_gazebo(self):
        pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
        rospy.init_node('talker', anonymous=True)
        rate = rospy.Rate(10) # VERNYT 10!!!

        self.model_position()
        self.distance_between()
        self.calculate_movement()

        twist = Twist()
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0

        while not rospy.is_shutdown():

            self.model_position()
            self.distance_between()
            print('dist  x' + str(self.x_d) + 'y' + str(self.y_d))
            self.speed_reduction()
            print('speed2  x' + str(self.x_speed) + 'y' + str(self.y_speed))
            twist.linear.x = self.x_speed * self.speed
            twist.linear.y = self.y_speed * self.speed
            print('twist:  x' + str(twist.linear.x) + 'y' +str(twist.linear.y))
            
            if self.abs_xd > 0.06 or self.abs_yd > 0.06:
                pub.publish(twist)
                rate.sleep()
            else:
                break

if __name__ == "__main__":

    #user inputs the values of x, y, and speed
    x = int(sys.argv[1])
    y = int(sys.argv[2])
    speed = abs(int(sys.argv[3]))

    if speed != 0:
        gaz = GazeboMovements(x, y, speed)
        gaz.movements_gazebo()
    else:
        print("Input speed > 0!")
