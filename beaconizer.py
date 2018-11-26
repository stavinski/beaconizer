#!/usr/bin/env python
# coding=utf-8

# Todo:
#
# Proper threading
# Tweak timings with testing against different clients

__description__ = "beaconizer"
__author__ = "Mike Cromwell"
__version__ = "1.0.0"
__date__ = "2018/11/22"


import threading
import time
import sys

from argparse import ArgumentParser, FileType
from scapy.all import *
from wifi import WifiInterface


# globals
probes = set()
ssids = []
args = {}

# defaults
IFACE_DEFAULT = 'wlan0'
CHANNEL_DEFAULT = 11


def sniff_probe(pkt):
  if pkt.haslayer(Dot11ProbeReq):
    name=pkt[Dot11ProbeReq].info
    if len(name) > 0 and not name in probes:
      probes.add(name)
      mac_src=pkt[Dot11].addr2
      escaped_name=name.replace("'","''")      
      print >> args.outfile, "'%s', %s" % (escaped_name, mac_src)
      

def sniff_probes():
  sniff(prn=sniff_probe, filter="wlan type mgt subtype probe-req", store=False)


def send_beacons():

  while True:
    for ssid in ssids:

      dot11 = Dot11(type=0, subtype=8, addr1='ff:ff:ff:ff:ff:ff',
      addr2=str(RandMAC()), addr3=str(RandMAC()))
      beacon = Dot11Beacon(cap='ESS')
      essid = Dot11Elt(ID='SSID', info=ssid, len=len(ssid))

      frame = RadioTap()/dot11/beacon/essid
      sendp(frame)
      time.sleep(1)
   

def main():
  
  # scapy setup
  conf.verb = False
  conf.iface = args.iface

  # wifi setup
  wifi_iface = WifiInterface(args.iface)
  wifi_iface.set_monitor()
  wifi_iface.set_channel(args.channel)

  try:
    
    for ssid in args.ssids:
      ssids.append(ssid.rstrip('\n'))

    t_probes=threading.Thread(target=sniff_probes)
    t_probes.daemon = True
    t_probes.start()
    send_beacons()

  except KeyboardInterrupt:
    print "[!] CTRL-C pressed, exiting!"
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

  args = parser.parse_args()          
  main()
