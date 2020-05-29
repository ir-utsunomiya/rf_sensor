#!/usr/bin/env python3

#****************************************************
# Class for manipulating wifi interfaces with shared memory
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
from rf_sensor.WiFiDevice import WiFiDevice

class MultiWiFiDevice:
    def __init__(self,**kwargs):
        self.iface_list    = kwargs.pop('iface_list',('wlp5s0',))
        self.channel_list = kwargs.pop('channel_list', (1,))
        self.data = kwargs.pop('data',None)
        self.ts = kwargs.pop('ts',1.0)

        # processes
        self.sample_process = None

        # variables
        if self.data is None: self.data = multiprocessing.Manager().list()
        kwargs['data']=self.data # so all devices share the same list

        # WiFi devices
        assert len(self.iface_list)==len(self.channel_list)
        self.wifi_devices = list()
        for iface, channel in zip(self.iface_list, self.channel_list):
            kwargs_i = kwargs
            kwargs_i['iface'] = iface
            kwargs_i['channels'] = (channel,)

            self.wifi_devices.append(WiFiDevice(**kwargs_i))

    # samples all interfaces at a fixed sampling time (ts)
    ## public functions
    def sample(self):
        for wifi in self.wifi_devices:
            if wifi.read_alive() is False : wifi.read_start()

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
        if self.sample_alive() is True: print('Terminating sample'); self.sample_process.terminate()

        for wifi in self.wifi_devices:
            wifi.terminate()