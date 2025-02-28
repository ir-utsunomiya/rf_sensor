#include <iostream>
#include <thread>
#include <atomic>
#include <csignal>
#include <pthread.h>
#include <unistd.h>

#include <ros/ros.h>
#include "std_msgs/Int32.h"

float rate = 10;
int off_flag = 0;

std::atomic<int> on_flag(0);
std::atomic<int> input_count(0);


void waitEnter()
{
    while (ros::ok())
    {
        std::cin.get();
        input_count++;
        if (input_count % 2 == 1)
        {
            on_flag++;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

int main(int argc, char **argv) {
    ros::init(argc, argv, "directional_strength_test");
    ros::NodeHandle nh;

    ros::Publisher pub = nh.advertise<std_msgs::Int32>("angle_flag", 10);
    ros::Rate r(rate);
    std_msgs::Int32 flag;

    std::thread inputThread(waitEnter);

    while (ros::ok())
    {
        int judgment = input_count % 2;

        switch (judgment)
        {
            case 0:
                flag.data = off_flag;
                break;
            case 1:
                flag.data = on_flag;
                break;
        }
        std::cout << "angle_flag : " << flag.data << std::endl;
        pub.publish(flag);
        r.sleep();
    }

    inputThread.join();
    return 0;
}