#!/usr/bin/python3

import numpy as np
import sys
import subprocess
import os
import logging


def pcap_extract(files):
    Rss = list()
    files_ = list()

    for f in files:
        if os.path.isdir(f): 
            tmp = os.listdir(f)
            for tmpf in tmp:            
                if tmpf.endswith('.pcap'): files_.append(f+tmpf)
        else: files_.append(f)

    for f in files_:
        logging.info('Processing {:s}'.format(f))
        cmd = 'tcpdump -r {:s}'.format(f)

        try:
            pcap = subprocess.check_output(cmd,shell=True,stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            logging.warning('Could not process file {:s} - returned with error (code {})'.format(f, e.returncode))
            logging.debug('[pcap_extract] [Error] {}'.format(e.output))

        pcap = str(pcap).split('\\n')
        for l in pcap:
            try: 
                w = str(l).split()
                rss = list()
                t_s = w[0].split(':')
                t_s = int(t_s[0])*3600+int(t_s[1])*60+float(t_s[2]) 
                            
                for i in range(len(w)):
                    if 'MHz' in w[i]: freq = int(w[i-1]) 
                    if 'dBm' in w[i]: rss.append(int(w[i].split('dBm')[0]))
                    if 'Beacon' in w[i]: mac = w[i+1]    
                Rss.append([t_s,freq,mac,np.asarray(rss)])
            except:
                pass
    
    #for rss in Rss:
    #    print('{:6f}, {:4d}, {:20s}, {:}'.format(*rss))
    
    return Rss
    
if __name__ == '__main__':
    files = sys.argv[1:]#sys.stdin
    pcap_extract(files)
    
