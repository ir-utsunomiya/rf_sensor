execute_process(COMMAND "/home/nanakubo/catkin_ws/src/rf_sensor/build/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/nanakubo/catkin_ws/src/rf_sensor/build/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
