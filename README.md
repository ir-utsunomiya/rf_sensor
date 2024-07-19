# rf_sensor
ROS node for radio frequency based sensors


Python scripts on [src/rf_sensor](https://github.com/ir-utsunomiya/rf_sensor/tree/main/src) can be used to run rf_sensor without ROS. <br/>
See [notebooks/Standalone rf_sensor.ipynb](https://github.com/ir-utsunomiya/rf_sensor/blob/main/notebooks/Standalone%20rf_sensor.ipynb) for examples on how to use them.

## Dependency
* ROS node [`rf_msgs`](https://github.com/ir-utsunomiya/rf_msgs) containing ROS message definitions

## Running iwconfig and ifconfig as passwordless sudo
It is recommended to modify sudoers to allow your user to run ifconfig and iwconfig as sudo without password.
If the node is run with rosrun there are no issues. Password is asked once.
However, when run from roslaunch it asks every time (in a loop) so not practical. No idea what is causing this behaviour

To modify your sudoer
```
sudo visudo 
```
Go to the end of the file and add

```
your_user_name ALL=(root) NOPASSWD: /sbin/iwconfig, /sbin/ifconfig
```

replace `your_user_name` by the name of your user

