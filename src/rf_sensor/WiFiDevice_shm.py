# Copyright (c) 2019, the rf_sensor authors (see AUTHORS.txt)
# Licensed under the BSD 3-clause license (see LICENSE.txt)

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
import ctypes
import sysv_ipc

MAX_WIFI_LEN = 500
MIN_READINGS = 5

class mac(ctypes.Structure):
    #macs have 17 characters (can be further compressed if necessary)
    _fields_ = [
        ('mac', ctypes.c_char*17)
    ]

class wifid(ctypes.Structure):
    _fields_ = [
        ('seq', ctypes.c_uint32),
        ('data', ctypes.c_float*MAX_WIFI_LEN),
        ('nap', ctypes.c_uint16),
        ('mac', mac*MAX_WIFI_LEN) 
    ]

class WiFiDeviceSHM(WiFiDevice):
    def __init__(self,**kwargs):
        WiFiDevice.__init__(self,**kwargs)
        self.shm_id = kwargs.get('shm_id',1001)
        self.mac_dict = kwargs.get('mac_dict',dict())
        self.update_dict = kwargs.get('update_dict',True)
        
        # shm
        libc_path = ctypes.util.find_library("c")
        libc = ctypes.CDLL(libc_path)
        shmget = libc.shmget
        shmat = libc.shmat
        shmat.restype = ctypes.c_long # default does not work for 64bit sys

        size = ctypes.sizeof(wifid)
        mem_id = shmget(self.shm_id,size,sysv_ipc.IPC_CREAT | 0o666)
        print('shm_id={:d}, mem_id={:d}'.format(self.shm_id,mem_id))
        shmptr = shmat(mem_id,None,0)
        print('pointer',shmptr)
        self.wifid_ptr = ctypes.cast(shmptr, ctypes.POINTER(wifid))

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
        nap = len(self.mac_dict)
        seq = 0
        while True:
            time.sleep(self.ts)
            #if not enough data points, do not update shm, wait for more samples
            if len(self.data) > 5:
                z = np.zeros(MAX_WIFI_LEN) # erase previous data
                count = np.zeros(MAX_WIFI_LEN)

                for datum in self.data:
                    index = None
                    try:
                        index = self.mac_dict[datum[2]]
                    except:
                        # not found in the dictionary
                        if self.update_dict:
                            self.mac_dict[datum[2]] = nap
                            index = nap
                            self.wifid_ptr.contents.mac[nap].mac = datum[2]
                            nap += 1
                    if index is not None:
                        z[index] += datum[3][0]
                        count[index] +=1
                self.data[:] = []

                # publish shm
                self.wifid_ptr.contents.seq = seq
                self.wifid_ptr.contents.nap = nap
                index = np.where(z!=0)[0]
                for i in index:
                    self.wifid_ptr.contents.data[i] = 100+1.*z[i]/count[i] # 100 is added so values are from zero to 100
                
                # update seq
                seq += 1

    def shm_print(self):
        print('{:18s}: '.format('Sequence'), self.wifid_ptr.contents.seq)
        print('{:18s}: '.format('N access points'),self.wifid_ptr.contents.nap)
        print('{:18s}: '.format('data'), self.wifid_ptr.contents.data[:self.wifid_ptr.contents.nap])
        print('{:18s}: '.format('mac address dictionary'))
        for index in range(self.wifid_ptr.contents.nap):
            print(self.wifid_ptr.contents.mac[index].mac)
