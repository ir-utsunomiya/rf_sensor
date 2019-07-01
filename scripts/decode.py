import numpy as np
import sys

def tcp2matrix(stream):
    #verbose = kwagrgs.get('verbose',True)

    Rss = list()
    for l in stream.readlines():
        #print(l)
        w = str(l).split()
        rss = list()
        for i in range(len(w)):
            if 'MHz' in w[i]: freq = int(w[i-1]) 
            if 'dBm' in w[i]: rss.append(int(w[i].split('dBm')[0]))
            if 'Beacon' in w[i]: mac = w[i+1]    
        Rss.append([freq,mac,np.asarray(rss)])
 
    for rss in Rss:
        print('{:4d}, {:20s}, {:}'.format(*rss))

    return Rss
    
if __name__ == '__main__':
    stream = sys.stdin#sys.argv[1:]
    print(stream)
    tcp2matrix(stream)
    
