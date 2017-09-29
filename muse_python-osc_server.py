import argparse
import math

from pythonosc import dispatcher
from pythonosc import osc_server


def eeg_handler(unused_addr, args, ch1, ch2, ch3, ch4, foo):
#    print("EEG (uV) per channel: ", ch1, ch2, ch3, ch4, foo)
    print("{},{},{},{},{}".format(ch1, ch2, ch3, ch4, foo))

def eeg_handler2(*args):
#    print("EEG (uV) per channel: ", ch1, ch2, ch3, ch4, foo)
    #print("{},{},{},{},{}".format(ch1, ch2, ch3, ch4, foo))
    for arg in args:
        print(arg, end=',')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="192.168.1.176",
                        help="The ip to listen on")
    parser.add_argument("--port",
                        type=int,
                        default=5000,
                        help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/debug", print)
    dispatcher.map("/muse/eeg", eeg_handler, "EEG")

    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    #print("Serving on {}".format(server.server_address))
    server.serve_forever()
