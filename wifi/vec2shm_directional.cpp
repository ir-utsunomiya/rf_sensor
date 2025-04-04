// standard lib
#include <iostream>
#include <vector>

// ros lib
#include <ros/ros.h>
#include <std_msgs/Float32MultiArray.h>

// irlab lib
extern "C" {
#include "shm.h"
#include "unistd.h"
}

#define WIFI_DIRECTIONAL_SHM_ID 20241219
#define NUM_TOPICS 8
#define MAX_DATA_SIZE 1000

typedef struct {
    int naps[NUM_TOPICS];
    float data[NUM_TOPICS][MAX_DATA_SIZE];
} VecshmDirectional;

// global def
int wifivec_directional_shm_id;
static VecshmDirectional *vecshm_directional;

void wifivecCallback(const std_msgs::Float32MultiArray::ConstPtr &msg, int topic_index) {
    size_t data_size = msg->data.size();
    vecshm_directional->naps[topic_index] = data_size;

    for (size_t i = 0; i < data_size; i++) { 
        vecshm_directional->data[topic_index][i] = msg->data[i];
        // std::cout << vecshm_directional->data[topic_index][i] << " " ;
    }

    // std::cout << std::endl;
    ROS_INFO("wifivec callback for topic index: %d", topic_index + 1);
}

int main(int argc, char **argv) {
    ros::init(argc, argv, "vecshm_directional");
    ros::NodeHandle nh;

    nh.param<int>("wifivec_shm_id", wifivec_directional_shm_id, WIFI_DIRECTIONAL_SHM_ID);
    vecshm_directional = (VecshmDirectional *)shm_get_buf(wifivec_directional_shm_id, sizeof(VecshmDirectional));

    std::vector<ros::Subscriber> subscribers;

    std::vector<std::string> topic_names = {"/rss_vec_directional_1",
                                            "/rss_vec_directional_2",
                                            "/rss_vec_directional_3",
                                            "/rss_vec_directional_4",
                                            "/rss_vec_directional_5",
                                            "/rss_vec_directional_6",
                                            "/rss_vec_directional_7",
                                            "/rss_vec_directional_8"};

    for (int i = 0; i < NUM_TOPICS; i++) {
        subscribers.push_back(nh.subscribe<std_msgs::Float32MultiArray>(topic_names[i], 10, boost::bind(wifivecCallback, _1, i)));
    }

    ros::spin();

    return 0;
}
