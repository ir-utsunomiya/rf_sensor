//standard lib
#include <iostream>

//ros lib
#include <ros/ros.h>
#include "ros/message.h"
#include <ros/console.h>
// #include <std_msgs/UInt8MultiArray.h>
#include <std_msgs/Float32MultiArray.h>
#include <geometry_msgs/PoseWithCovarianceStamped.h>

//irlab lib
extern "C" {
#include "shm.h"
#include "unistd.h"
}

#define WIFI_DEFAULT_SHM_ID 1001
#define AMCL_POSE_SHM_ID 1101

typedef struct{
int seq;
int nap;
float data[];
} Vecshm;

typedef struct{
_Float64 x, y, t;
} Amclpose;

//global def
int wifivec_shm_id;
int amclpose_shm_id;

static Vecshm *vec2shm;
static Amclpose *amcl_pose;

void wifivecCallback(const std_msgs::Float32MultiArray::ConstPtr& msg)
{
    for(size_t i = 0; i < msg->data.size(); ++i){
        vec2shm->data[i] = msg->data[i];
        }
    vec2shm->nap = msg->data.size();
    ROS_INFO("wifivec callback");
}

void amclposeCallback(const geometry_msgs::PoseWithCovarianceStamped::ConstPtr& msg)
{
    amcl_pose->x = msg->pose.pose.position.x;
    amcl_pose->y = msg->pose.pose.position.y;
    amcl_pose->t = msg->pose.pose.orientation.z;
    ROS_INFO("amcl pose callback");
}

int main(int argc, char **argv)
{
    ros::init(argc, argv, "vec2shm");
    ros::NodeHandle nh;
    nh.param<int>("wifivec_shm_id", wifivec_shm_id ,WIFI_DEFAULT_SHM_ID);
    nh.param<int>("amclpose_shm_id", amclpose_shm_id ,AMCL_POSE_SHM_ID);
    
    amcl_pose = (Amclpose*)shm_get_buf(amclpose_shm_id, sizeof(Amclpose));
    vec2shm = (Vecshm*)shm_get_buf(wifivec_shm_id, sizeof(Vecshm));
    
    ros::Subscriber sub_wifi = nh.subscribe("/rss_vec", 10, wifivecCallback);
    ros::Subscriber sub_pose = nh.subscribe("/amcl_pose",10,amclposeCallback);

    while(ros::ok()){
        ros::spinOnce();
    }
    return 0;
}