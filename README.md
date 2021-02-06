# raspicam-stream

Run the client on Pi and server on laptop. Need matplotlib on laptop.

If MPTCP is present on both devices and configured correctly, MPTCP will be used. I am using roundrobin on Pi and redundant scheduler on laptop. Defaults should also work. 

Incase MPTCP is not present, regular TCP will be used.
