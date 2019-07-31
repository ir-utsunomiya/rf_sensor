# Single RSS reading from tcpdump
# Depending on your wireless interface/driver
# you may get more than one rss measurement per packet

Header header  # It is preferable that the recorded time is that by ros, not tcpdump, 
               # as the device recording the packet may not be syncronized with the host

string mac_address    # mac address of received signal
int16 freq            # frequency in Hz of the received signal
int8[]  data          # 1 or more signal strength values
                      # for more than 1 value

