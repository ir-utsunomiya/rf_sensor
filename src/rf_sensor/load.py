import rosbag
import tf
import numpy as np
import pandas as pd

from .msg import Rss

def load_data(**kwargs):
    file_name = kwargs.get('file_name','paper_0_gt')
    file_path = kwargs.get('file_path','/data/bags/tsukuba_challenge/09_14/')
    bag = rosbag.Bag(file_path+file_name+'.bag')

    # rss
    rss_secs   = list()
    rss_nsecs  = list()
    rss_mac    = list()
    rss_freq   = list()
    rss_data   = list()

    for topic, msg, t in bag.read_messages(topics=['rss','/rss']):
        rss_secs.append(msg.header.stamp.secs)
        rss_nsecs.append(msg.header.stamp.nsecs)
        rss_mac.append(msg.mac_address)
        rss_freq.append(msg.freq)
        rss_data.append((msg.data[0]+95)/95.) #as of now only using the first rss measurement
                                 #to use all measurements maybe convert msg.data tuple to np array

    rss_secs  = np.asarray(rss_secs)
    rss_nsecs = np.asarray(rss_nsecs)
    rss_mac   = np.asarray(rss_mac)
    rss_freq  = np.asarray(rss_freq)
    rss_data  = np.asarray(rss_data)

    print('rss  #msgs: {:6d}'.format(rss_secs.shape[0]))

    # Try getting pose information if available
    # Pose
    pose_secs  = list()
    pose_nsecs = list()
    pose_x     = list()
    pose_y     = list()
    pose_yaw   = list()

    for topic, msg, t in bag.read_messages(topics=['amcl_pose','/amcl_pose']):
        pose_secs.append(msg.header.stamp.secs)
        pose_nsecs.append(msg.header.stamp.nsecs)
        pose_x.append(msg.pose.pose.position.x)
        pose_y.append(msg.pose.pose.position.y)
        #yaw angle
        rpy = tf.transformations.euler_from_quaternion((msg.pose.pose.orientation.x,
                                                        msg.pose.pose.orientation.y,
                                                        msg.pose.pose.orientation.z,
                                                        msg.pose.pose.orientation.w,
                                                        'xyzs'))
        pose_yaw.append(rpy[2])

    pose_secs  = np.asarray(pose_secs)
    pose_nsecs = np.asarray(pose_nsecs)
    pose_x     = np.asarray(pose_x)
    pose_y     = np.asarray(pose_y)
    pose_yaw   = np.asarray(pose_yaw)
    print('Pose #msgs: {:6d}'.format(pose_secs.shape[0]))

    if pose_secs.shape[0] > 0:
        # Getting corresponding rss_pose from pose msgs
        time_offset_ = np.min((rss_secs[0],pose_secs[0]))
        pose_time_   = int(1e9)*(pose_secs-time_offset_)+pose_nsecs
        rss_time_    = int(1e9)*(rss_secs-time_offset_)+rss_nsecs
        ## interpolating x-y
        rss_x   = np.interp(rss_time_,pose_time_,pose_x)
        rss_y   = np.interp(rss_time_,pose_time_,pose_y)
        ## interpolating angle
        yaw_x_  = np.interp(rss_time_,pose_time_,np.cos(pose_yaw))
        yaw_y_  = np.interp(rss_time_,pose_time_,np.sin(pose_yaw))
        rss_yaw = np.arctan2(yaw_y_,yaw_x_)
    else:
        rss_x = None
        rss_y = None
        rss_yaw = None

    rss_df = pd.DataFrame.from_dict({
        'secs':rss_secs,
        'nsecs':rss_nsecs,
        'mac_address':rss_mac,
        'freq':rss_freq,
        'data':rss_data,
        'x': rss_x,
        'y': rss_y,
        'yaw': rss_yaw
    })

    return rss_df
