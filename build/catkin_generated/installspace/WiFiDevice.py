# Copyright (c) 2019, the rf_sensor authors (see AUTHORS.txt)
# Licensed under the BSD 3-clause license (see LICENSE.txt)

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
    print("{:40s} ".format(cmd))
    while os.system(cmd):
        counter += 1
        print("\n[{:02d}/{:02d}] {:s} Failed".format(counter, max_counter, cmd))
        if counter >  max_counter : print('\n[Error] Max trial reached'); return 1
    print("OK")
    return 0

class WiFiDevice:
    """
    Base class to listen wireless devices
    Parameters:
        iface: (string) wireless interface name. Check available interfaces and their names using `iwconfig`
        channels: (list of ints) channels to listen (1-11)
        chopper_ts: (int/float) sampling time in seconds for channel hopper to go through all channels. If ts:1s and there are 2 channels, each channel gets 0.5s
        filter: (string) filters for tcpdump. default: Beacon, listens only to beacon frames. 
        ts: (int/float) sampling time in seconds for sample functions 
    Functions:
        chopper_start:
            starts channel hopping if desired
        tcpdump_start:
            starts wifi data aquisition
        read_start:
            starts tcpdump_start, 
            extracts main information and stores it in data array
        sample:
            starts read_start
            clears data every specified sampling time
        *_alive: 
            * is chopper/tcpdump/read/sample
            checks if process has started
        terminate:
            ends all processes
    """
    def __init__(self,**kwargs):
        self.iface = kwargs.get('iface','wlp5s0')
        self.channels = kwargs.get('channels', (1,6,11))
        self.chopper_ts = kwargs.get('channel_hopper_sampling_time',1.0)
        self.filter = kwargs.get('filter','Beacon')
        self.ts = kwargs.get('sampling_time',self.chopper_ts)
        self.data = kwargs.get('data',None)

        # variables
        if self.data is None: self.data = multiprocessing.Manager().list()

        # filters
        if self.filter == 'Beacon': self.filter = ' type mgt subtype beacon'

        # processes
        self.chopper_process = None
        self.tcpdump_process  = None
        self.read_process = None
        self.sample_process = None

        
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
        # set interface to first channel in channels
        if execute_retry("sudo -S iwconfig {:s} channel {:d}".format(self.iface,self.channels[0])) != 0     : return 1
        return 0

    # Channel Hopping 
    ## public functions
    def chopper_start(self):
        #self.cmd = "rosrun rf_sensor channel_hopper.py -i {} -t {} -ch {}".format(self.iface,1.*self.chopper_ts," ".join(str(ch) for ch in self.channels))
        
        if self.chopper_process is not None: self.chopper_process.terminate()
        try:
            self.chopper_process = multiprocessing.Process(target=self.__chopper)
            self.chopper_process.start()
        except:
            print('[Error] multiprocessing.Process(chopper_run) failed')

        print('Channel Hopper Initialized')
        return 0
    
    def chopper_alive(self):
        try: return self.chopper_process.is_alive()
        except: return False
    
    ## private function
    def __chopper(self):
        ts = 1.0*self.chopper_ts/len(self.channels)
        ret = 0
        while(not ret):
            for ch in self.channels:
                ret = os.system("sudo -S iwconfig {:s} channel {:d}".format(self.iface,ch))
                if ret != 0 : print('[Error] Channel hopper could not change channel. Are you running as sudo?')
                time.sleep(ts)

    # tcpdump wrapper
    ## public functions
    def tcpdump_start(self):
        """
        iface must be initialized before with init(iface)
        """
        cmd = 'sudo -S tcpdump -i {:s} -ne --time-stamp-precision=micro -l --immediate-mode {:s}'.format(self.iface,self.filter)
        self.tcpdump_process = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)
        print('tcpdump process initialized')
        return 0

    def tcpdump_alive(self):
        try: return self.tcpdump_process.poll() is None
        except: return False

    # WiFi data decoding
    ## public functions
    def read_start(self):
        """
        continuously decodes incomming tcpdump messages and publishes to data list 
        """
        if self.tcpdump_alive() is False: self.tcpdump_start()
        self.read_process = multiprocessing.Process(target=self.__decode)
        self.read_process.start()
        print('RSS messages stored at data')
        return 0

    def read(self):
        """
        outputs last message only
        """
        if self.tcpdump_alive() is False : self.tcpdump_start()
        print(self.tcpdump_process.stdout.readline())

    def read_alive(self):
        try: return self.read_process.is_alive() is True
        except: return False
    
    ## private function
    def __decode(self,verbose=False):
        """
        decodes tcpdump message to data list
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

    # samples at a fixed sampling time (ts)
    ## public functions
    def sample(self):
        if self.read_alive() is False : self.read_start()
        try:
            self.sample_process = multiprocessing.Process(target=self.__sample)
            self.sample_process.start()
        except:
            print('[Error] multiprocessing.Process(sample_process) failed')

        print('Sampling every {:f} s'.format(self.ts))
        return 0
    
    def sample_alive(self):
        try: return self.sample_process.is_alive()
        except: return False

    ## private function
    def __sample(self):
        while True:
            time.sleep(self.ts)
            self.data[:] = []

    def terminate(self):
        print('Terminating Processes')
        if self.sample_alive() is True: print('Terminating sample'); self.sample_process.terminate()
        if self.read_alive() is True: print('Terminating read'); self.read_process.terminate()
        if self.chopper_alive() is True:  print('Terminating chopper'); self.chopper_process.terminate()
        if self.tcpdump_alive() is True: 
            print('Terminating tcpdump')
            cmd = "sudo kill -9 {:d}".format(self.tcpdump_process.pid)
            os.system(cmd)
            if self.tcpdump_alive() is True:
                print("Could not kill the process, please try")
                print("    ",cmd)
