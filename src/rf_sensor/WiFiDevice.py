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
import sys, os
import subprocess, multiprocessing
import datetime, time
import numpy as np

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


    chopper_start:
        starts channel hopping if desired
    tcpdump_start:
        starts wifi data aquisition
    read_start:
        starts tcpdump_start, 
        extracts main information and stores it in data array
    sampling:
        starts read_start
        clears data every specified sampling time
    """
    def __init__(self,**kwargs):
        self.iface = kwargs.get('iface','wlp5s0')
        self.channels = kwargs.get('channels', (1,6,11))
        self.chopper_ts = kwargs.get('channel_hopper_sampling_time',1.0)
        self.filter = kwargs.get('filter','Beacon')
        self.ts = kwargs.get('sampling_time',self.chopper_ts)

        # filters
        self.filter_cmd = ''
        if self.filter == 'Beacon': self.filter_cmd += ' type mgt subtype beacon'

        # processes
        self.chopper_process = None
        self.tcpdump_process  = None
        self.read_process = None
        self.sample_process = None

        # variables
        self.data = multiprocessing.Manager().list()

        if self.init_device() == 0: print('\nDevice Initialized')
        else: print('[Error] Device initialization failed')
        

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
                if ret != 0 : print('[Error] Channel hopper could not change channel. Are you running as sudo?')
                time.sleep(ts)

    def chopper_start(self):
        #self.cmd = "rosrun rf_sensor channel_hopper.py -i {} -t {} -ch {}".format(self.iface,1.*self.chopper_ts," ".join(str(ch) for ch in self.channels))
        
        if self.chopper_process is not None: self.chopper_process.terminate()
        try:
            self.chopper_process = multiprocessing.Process(target=self.chopper_cmd_)
            self.chopper_process.start()
        except:
            print('[Error] multiprocessing.Process(chopper_run) failed')

        print('Channel Hopper Initialized')
        return 0
    
    def chopper_alive(self):
        return self.chopper_process.is_alive()

    def tcpdump_start(self):
        """
        iface must be initialized before with init(iface)
        """
        cmd = 'sudo -S tcpdump -i {:s} -ne --time-stamp-precision=micro -l --immediate-mode {:s}'.format(self.iface,self.filter_cmd)
        self.tcpdump_process = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)
        print('tcpdump process initialized')
        return 0

    def tcpdump_alive(self):
        return self.tcpdump_process.poll() is None

    def read_start(self):
        if not self.tcpdump_alive(): self.tcpdump_start()
        self.read_process = multiprocessing.Process(target=self.decode)
        self.read_process.start()
        print('RSS messages stored at data')
        return 0

    def read_alive(self):
        return self.read_process.is_alive()

    def decode(self,verbose=False):
        """
        tcpdump should be running
        """
        while True:
            rss_data = list()
            s = 0
            try:
                tmp = self.tcpdump_process.stdout.readline()
                tmp = tmp.split()
                for i in range(len(tmp)):
                    if b'MHz' in tmp[i]: freq = int(tmp[i-1]); s+=10
                    if b'dBm' in tmp[i]: rss_data.append(int(tmp[i].split(b'dBm')[0])); s+=1
                    if b'BSSID' in tmp[i]: mac = tmp[i].split(b'BSSID:')[1]; s+=10
                if verbose: print(s)
                if s>=21: 
                    self.data.append(list([datetime.datetime.utcnow(), freq, mac, np.asarray(rss_data)]))
                    if verbose: print(self.data[-1])
                else: print('Incomplete rss msg')
            except:
                print('[Error] Could not decode rss data')
            time.sleep(1/500.) #refresh at 500Hz

    def read(self):
        """
        tcpdump should be running
        """
        if self.tcpdump_alive() is False : self.tcpdump_start()
        print(self.tcpdump_process.stdout.readline())

    def sample_(self):
        while True:
            time.sleep(self.ts)
            self.data[:] = []

    def sample(self):
        if self.read_alive() is False : self.read_start()
        try:
            self.sample_process = multiprocessing.Process(target=self.sample_)
            self.sample_process.start()
        except:
            print('[Error] multiprocessing.Process(sample_process) failed')

        print('Sampling every {:f} s'.format(self.ts))
        return 0


    def terminate(self):
        self.chopper_process.terminate()
        #self.tcpdump_process.terminate()
        self.read_process.terminate()