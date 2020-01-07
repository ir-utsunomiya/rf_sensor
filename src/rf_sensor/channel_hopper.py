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

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Easy Channel Hopper')
    parser.add_argument('-i',dest='iface',default='wlp5s0',help='wlan interface name')
    parser.add_argument('-t',dest='sampling_time',type=float,default=1.0,help='Total sample time of a hoop')
    parser.add_argument('-ch',dest='channels',type=int,nargs='+',default=(1,6,11,),help='Channels to hop')
    parser.add_argument('-v',dest='verbose',type=bool,default=True)    
    args = parser.parse_args()
    
    if args.verbose: 
        for k in args.__dict__: print('{:15s} \t'.format(k),args.__dict__[k])

    ts = args.sampling_time/len(args.channels)
    while(True):
        for ch in args.channels:
            os.system("sudo -S iwconfig {:s} channel {:d}".format(args.iface, ch))
            time.sleep(ts)
