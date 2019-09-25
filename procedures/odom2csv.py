#!/usr/bin/env python
import sys
import rospy
from nav_msgs.msg import Odometry

args = sys.argv

out = None

def callback(data):


    with open(output_file, "a") as out:
        print(data.pose.pose.position.x, data.pose.pose.position.y)
        out.write(",".join([str(data.pose.pose.position.x), str(data.pose.pose.position.y)]))
        out.write("\n")
    
def listener():

    # in ROS, nodes are unique named. If two nodes with the same
    # node are launched, the previous one is kicked off. The 
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaenously.
    rospy.init_node('odom_listener', anonymous=True)

    rospy.Subscriber("/odom", Odometry, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()
        
if __name__ == '__main__':
    output_file=args[1]
    out = open(output_file, "a")
    listener()
    out.close()
