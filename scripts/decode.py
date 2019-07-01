import numpy as np
import sys

def tcp2matrix(stream):
    #verbose = kwagrgs.get('verbose',True)

    Rss = list()
    for l in stream.readlines():
        print(l)
        w = str(l).split()
        rss = list()
        t_s = w[0].split(':')
        t_s = int(t_s[0])*3600+int(t_s[1])*60+float(t_s[2]) 
                    
        for i in range(len(w)):
            if 'MHz' in w[i]: freq = int(w[i-1]) 
            if 'dBm' in w[i]: rss.append(int(w[i].split('dBm')[0]))
            if 'Beacon' in w[i]: mac = w[i+1]    
        Rss.append([t_s,freq,mac,np.asarray(rss)])
 
    for rss in Rss:
        print('{:6f}, {:4d}, {:20s}, {:}'.format(*rss))

    return Rss
    
if __name__ == '__main__':
    stream = sys.stdin#sys.argv[1:]
    print(stream)
    tcp2matrix(stream)
    
