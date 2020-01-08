#!/usr/bin/env python

#****************************************************
# Easy Channel Hopper
# Input:
#   -i, iface:          wireless interface name
#   -c, channels:       channels to survey
#   -t, sampling_time:  Total time to go through all channels
# Output: None, program runs until interrupted
#               making the desired interface go through
#               the selected channels
#****************************************************

from __future__ import print_function
import argparse
import time
import os

class ChannelHopper:
    """
    Base class to set Wireless Device to hop channels
    """
    def __init__(self,**kwargs):
        self.iface          = kwargs.get('iface','wlp5s0')
        self.sampling_time  = kwargs.get('sampling_time',1.0)
        self.channels       = kwargs.get('channels',(1,6,11))

        self.iface = self.iface.split()[0] # to avoid code injection

    def run(self):
        ts = 1.0*self.sampling_time/len(self.channels)
        while(True):
            for ch in self.channels:
                os.system("sudo -S iwconfig {:s} channel {:d}".format(self.iface,ch))
                time.sleep(ts)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Easy Channel Hopper')
    parser.add_argument('-i',dest='iface',default='wlp5s0',help='wlan interface name')
    parser.add_argument('-t',dest='sampling_time',type=float,default=1.0,help='Total sample time of a hoop')
    parser.add_argument('-ch',dest='channels',type=int,nargs='+',default=(1,6,11,),help='Channels to hop')
    parser.add_argument('-v',dest='verbose',type=bool,default=True)
    args = parser.parse_args()

    if args.verbose:
        for k in args.__dict__: print('{:15s} \t'.format(k),args.__dict__[k])

    chopper = ChannelHopper(**vars(args))
    chopper.run()
