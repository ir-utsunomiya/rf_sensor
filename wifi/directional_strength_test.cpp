#include <iostream>
#include <thread>
#include <atomic>
#include <csignal>
#include <pthread.h>
#include <unistd.h>

#include <ros/ros.h>
#include "std_msgs/Float32.h"  // Float32型に変更

float rate = 10;
std::atomic<int> input_count(0);

void waitEnter()
{
    while (ros::ok())
    {
        std::cin.get();  // Enter入力待ち
        input_count++;
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

int main(int argc, char **argv) {
    ros::init(argc, argv, "directional_strength_test");
    ros::NodeHandle nh;

    ros::Publisher pub = nh.advertise<std_msgs::Float32>("angle_flag", 10);
    ros::Rate r(rate);
    std_msgs::Float32 flag;

    std::thread inputThread(waitEnter);

    while (ros::ok())
    {
        int count = input_count.load();

        if (count % 2 == 0)
        {
            flag.data = 0.0;
        }
        else
        {
            // (count - 1) / 2 = 0,1,2,3,... → 1.0, 1.5, 2.0, ...
            flag.data = 1.0 + 0.5f * ((count - 1) / 2);
        }

        std::cout << "angle_flag : " << flag.data << std::endl;
        pub.publish(flag);
        r.sleep();
    }

    inputThread.join();
    return 0;
}
