import argparse
import math
import sys
import time
import numpy as np
import pandas as pd

from pythonosc import dispatcher
from pythonosc import osc_server

from seppuku import honor, HonorableError

def eeg_handler(unused_addr, args, ch1, ch2, ch3, ch4, foo):
#    print("EEG (uV) per channel: ", ch1, ch2, ch3, ch4, foo)
    print("{},{},{},{},{}".format(ch1, ch2, ch3, ch4, foo))

def eeg_handler2(*args):
    """First two fields are just metadata about the stream"""
#    print("EEG (uV) per channel: ", ch1, ch2, ch3, ch4, foo)
    #print("{},{},{},{},{}".format(ch1, ch2, ch3, ch4, foo))
    for arg in args[2:]:
        print(arg, end=',')
    print('\n', end='')
    # print(args[2:])

class EEGHandlerDF:
    def __init__(self, filename='eeg.csv', dumprate=100, argsize=5):
        self.filename = filename
        self.dumprate = dumprate  # ratio to which write to file
        self.argsize = argsize
        chs = list(range(argsize))
        self.header = ['time',] + ['ch{}'.format(n) for n in chs]
        self.data = pd.DataFrame(None, columns=self.header)
        self.packet = []
        self.i = 0
        self.j = 0
        self.state = 1

    def handle(self, *args, verbose=1):
        if self.state:
            print('first', args)
            self.state = 0
        try:
            now = int(time.time() * 1e9)
            packet = (now,) + args[2:]
            if verbose == 2:
                print(self.i, packet)
            self.packet.append(packet)


            if self.i >= self.dumprate:
                try:
                    frame = np.array(self.packet) # because of threading, weird mutation shit is going on here
                    self.packet = []
                    frame = pd.DataFrame(frame, columns=self.header)
                except Exception as exc:
                    raise HonorableError('error somewhere in packet framing', exc)

                self.data = self.data.append(frame)
                self.data.to_csv(self.filename)
                self.i = 0
                self.packet = []
                if verbose == 1:
                    print(self.j)
                self.j += 1


            self.i += 1
        except Exception as exc:
            raise HonorableError('error somewhere in handle()', exc)

if __name__ == "__main__":
    """The phone should be set to output to the IP address of the computer hosting the script. 
    That also means we should be listening on that same IP address """
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="192.168.1.13",
                        help="The ip to listen on (this should be computer's own IP)")
    parser.add_argument("--port",
                        type=int,
                        default=5336,
                        help="The port to listen on")
    args = parser.parse_args()

    handler = EEGHandlerDF(filename='output/eeg{}.csv'.format(int(time.time())))

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/debug", print)
    dispatcher.map("/muse/eeg", handler.handle, "EEG")



    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    #print("Serving on {}".format(server.server_address))
    server.serve_forever()

