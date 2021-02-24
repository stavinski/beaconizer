#!/usr/bin/env python3
# coding=utf-8


__description__ = "beaconizer"
__author__ = "Mike Cromwell"
__version__ = "2.0.0"
__date__ = "2021/02/24"


import time
import sys

from threading import Thread
from argparse import ArgumentParser, FileType
from scapy.all import *
from wifi import WifiInterface


# globals
ssids = []
args = {}

# defaults
IFACE_DEFAULT = 'wlan0'
CHANNEL_DEFAULT = 11

"""handles sniffing for probes in a thread context 
"""
class ProbeSniffingThread(Thread):
    
    def __init__(self):
        super(ProbeSniffingThread, self).__init__()        
        self._probes = set()
        self.daemon = True # we want to stop when parent thread stops
    
    def _packet_filter(self, pkt):
      if pkt.haslayer(Dot11ProbeReq):
        name = pkt[Dot11ProbeReq].info.decode()
        if len(name) > 0 and not name in self._probes:
          self._probes.add(name)
          mac_src = pkt[Dot11].addr2
          escaped_name = name.replace("'","''")      
          print("'%s', %s" % (escaped_name, mac_src), file=args.outfile)
        
    def run(self):
        sniff(prn=self._packet_filter, filter="wlan type mgt subtype probe-req", store=False)
                

def send_beacons():
  global ssids

  while True:
    for ssid in ssids:

      dot11 = Dot11(type=0, subtype=8, addr1='ff:ff:ff:ff:ff:ff',
      addr2 = str(RandMAC()), addr3=str(RandMAC()))
      beacon = Dot11Beacon(cap='ESS')
      essid = Dot11Elt(ID='SSID', info=ssid, len=len(ssid))

      frame = RadioTap()/dot11/beacon/essid
      sendp(frame)

      if args.verbose:
          print("[+] Sending {}".format(ssid), file=sys.stderr)

      time.sleep(1)
   

def main():
  global ssids
  
  # scapy setup
  conf.verb = False
  conf.iface = args.iface

  # wifi setup
  wifi_iface = WifiInterface(args.iface)
  wifi_iface.set_channel(args.channel)
  wifi_iface.set_monitor()
  
  try:
    ssids = [ssid.rstrip("\n") for ssid in args.ssids]    

    probe_thread = ProbeSniffingThread()
    probe_thread.start()
    send_beacons()

  except KeyboardInterrupt:
    print("[!] CTRL-C pressed, exiting!")
  finally:
    # set back
    wifi_iface.set_managed()


if __name__ == "__main__":
  if "linux" not in sys.platform:
    sys.exit("[!] only linux supported")

  if os.geteuid() != 0:
    sys.exit("[!] must be ran with root privileges")

  parser = ArgumentParser()
  parser.add_argument("ssids", type=FileType("r"), help="file with list of SSIDs to use, use - for STDIN", default=sys.stdin)
  parser.add_argument("-i", "--iface", help="wifi iface to use", default=IFACE_DEFAULT)
  parser.add_argument("-c", "--channel", help="channel to use", default=CHANNEL_DEFAULT)
  parser.add_argument("-o", "--outfile", type=FileType("w"), help="file to write output to, uses STDOUT by default", default=sys.stdout) 
  parser.add_argument("-v", "--verbose", help="Enable verbose logging to STDERR", action="store_true") 

  args = parser.parse_args()          
  main()
