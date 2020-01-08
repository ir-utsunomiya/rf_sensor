# rf_sensor
ROS node for radio frequency based sensors

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

