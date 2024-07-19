1. Copy rf_sensor to ~

2. It is recommended to 

Run ifconfig and iwconfig as sudo
It is recommended to modify sudoers to allow your user to run ifconfig, iwconfig and tcpdump as sudo without password. otherwise, calling functions that require sudo from notebook, does not work.

To modify your sudoer

sudo visudo

Go to the end of the file and add

your_user_name ALL=(root) NOPASSWD: /sbin/iwconfig, /sbin/ifconfig, /usr/sbin/tcpdump

replace your_user_name by the name of your user

3. Check your wifi device name
iwconfig

e.g.

lo        no wireless extensions.

wlx1cbfce958ca7  IEEE 802.11  Mode:Monitor  Frequency:2.412 GHz  Tx-Power=20 dBm   
          Retry short limit:7   RTS thr:off   Fragment thr:off
          Power Management:off
          
enp4s0    no wireless extensions.


>> The wifi device name would be "wlx1cbfce958ca7" in this case



To run

1. Start python2
python2

import sys
sys.path.append('~/rf_sensor') 
from WiFiDevice_shm import WiFiDeviceSHM
# Init device
wifi = WiFiDeviceSHM(iface='wlx1cbfce958ca7')
wifi.chopper_start()
# start sampling
wifi.sample()



Now it should be running, do not close python2
I will make a self contained example in the future, this should be ok for testing
