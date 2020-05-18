#!/usr/bin/env python3

#****************************************************
# Class for manipulating wifi interfaces
# Input:
#   -i, iface:      wireless interface name
#   -c, channels:   channels to survey
#   -f, filter:     filter applied to received packets
# Variables:
#   self.tcpdump_process is the process acquiring tcpdump data
#   to read use self.tcpdumpo_process.stdout.readline()
#****************************************************

#from __future__ import print_function
import sys
import os
import subprocess
import multiprocessing
import time

def execute_retry(cmd, max_counter = 10):
    counter = 0
    print("{:40s} ".format(cmd), end="\t")
    while os.system(cmd):
        counter += 1
        print("\n[{:02d}/{:02d}] {:s} Failed".format(counter, max_counter, cmd),end="")
        if counter >  max_counter : print('\n[Error] Max trial reached'); return 1
    print("OK")
    return 0

class WiFiDevice:
    """
    Base class to listen wireless devices
    """
    def __init__(self,**kwargs):
        self.iface = kwargs.get('iface','wlp5s0')
        self.channels = kwargs.get('channels', (1,6,11))
        self.chopper_ts = kwargs.get('channel_hopper_sampling_time',1.0)
        self.filter = kwargs.get('filter','Beacon')

        # filters
        self.filter_cmd = ''
        if self.filter == 'Beacon': self.filter_cmd += ' type mgt subtype beacon'

        self.chopper_process = None

        self.isCHopperRunning = False # Channel hopper running flag
        self.isTcpdumpRunning = False # Packages being acquired
        self.tcpdump_process  = None

        if self.init_device() == 0: print('\nDevice Initialized')
        else: return 1;

    def init_device(self):
        # turn the interface on/off to reset
        if execute_retry("sudo -S ifconfig {:s} down".format(self.iface)) != 0          : return 1
        if execute_retry("sudo -S ifconfig {:s} up".format(self.iface)) != 0            : return 1
        # change interface to monitor mode (off -> monitor mode -> on)
        if execute_retry("sudo -S ifconfig {:s} down".format(self.iface)) != 0          : return 1
        if execute_retry("sudo -S iwconfig {:s} mode monitor".format(self.iface)) != 0  : return 1
        if execute_retry("sudo -S ifconfig {:s} up".format(self.iface)) != 0            : return 1
        # set interface to default channel (1)
        if execute_retry("sudo -S iwconfig {:s} channel 1".format(self.iface)) != 0     : return 1
        return 0

    def chopper_cmd_(self):
        ts = 1.0*self.chopper_ts/len(self.channels)
        ret = 0
        while(not ret):
            for ch in self.channels:
                ret = os.system("sudo -S iwconfig {:s} channel {:d}".format(self.iface,ch))
                if ret != 0 : print('[Error] Channel hopper could not change channel. Are you running as sudo?');
                time.sleep(ts)

    def chopper_start(self):
        #self.cmd = "rosrun rf_sensor channel_hopper.py -i {} -t {} -ch {}".format(self.iface,1.*self.chopper_ts," ".join(str(ch) for ch in self.channels))
        
        if self.chopper_process is not None: self.chopper_process.terminate()
        try:
            self.chopper_process = multiprocessing.Process(target=self.chopper_cmd_)
            self.chopper_process.start()
        except:
            print('[Error] multiprocessing.Process(chopper_run) failed')

        self.isCHopperRunning = True
        return 0

    def tcpdump_start(self):
        """
        iface must be initialized before with init(iface)
        """
        cmd = 'sudo -S tcpdump -i {:s} -ne --time-stamp-precision=micro -l --immediate-mode {:s}'.format(self.iface,self.filter_cmd)
        self.tcpdump_process = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)
        self.isTcpdumpRunning = True

    def read(self):
        """
        tcpdump should be running
        """
        if self.isTcpdumpRunning:
            return self.tcpdump_process.stdout.readline()
        else:
            print('[Error] First run tcpdump_start')
