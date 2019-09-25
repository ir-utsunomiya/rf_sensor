# cartographer
```
cd ~/catkin_ws_tsukuba/src/tsukuba_challenge/launch
roslaunch sim.launch

```

# gmapping and amcl

## Preparation
please check bagfile, setting file

```
# bagfile location
export BAG_PATH=/mnt/rosbags/home/koda/rosbags/bagfiles/09_14

# Bagfile name
export BAG_NAME=XXXX

# prepare initial_condition file
cd ${BAG_PATH}/initial_conditions

cp -p paper_0.yaml ${BAG_NAME}

# map file location
cd ${BAG_PATH}/maps

```

## Implementation
```

export BAG_PATH=XXXX
export BAG_NAME=XXXX


# create map
roscd rf_sensor; cd launch

roslaunch build_map.launch bag_path:=${BAG_PATH} bag_name:=${BAG_NAME}

# static tf modified version
roslaunch build_map_01.launch bag_path:=${BAG_PATH} bag_name:=${BAG_NAME}

--> waiting to finish


# save map configuration
cd ${BAG_PATH}/maps
MAP_NAME=XXXX
e.g. MAP_NAME=${BAG_NAME}_map

rosrun map_server map_saver -f ${MAP_NAME}

--> and also save map png file in the same directory

# execute amcl
roscd rf_sensor; cd launch
roslaunch build_gt.launch bag_path:=${BAG_PATH} map_name:=${MAP_NAME} bag_name:=${BAG_NAME} 


### This is incorrect
#### visualize trajectory
###rosrun hector_trajectory_server hector_trajectory_server

# Output amcl_pose to csv file

# subscribe topic : /amcl_pose
python amclpose2csv.py ${BAG_PATH}/${BAG_NAME}_gt.csv

# subscribe topic : /odom
python odom2csv.py ${BAG_PATH}/${BAG_NAME}_gt.csv

--> waiting for finish

# check row count
rosbag info ${BAG_PATH}/${BAG_NAME}

wc -l paper01_gt.csv

```





