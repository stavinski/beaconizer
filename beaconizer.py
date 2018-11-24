#!/usr/bin/env python

# Todo:
#
# Allow options to be passed in
# Proper error handling
# better output for parsing
# Proper threading
# Tweak timings with testing against different clients


import threading
import time
import sys

from scapy.all import *

__NAME__ = """
 ______   _______  _______  _______  _______  _       _________ _______  _______  _______ 
(  ___ \ (  ____ \(  ___  )(  ____ \(  ___  )( (    /|\__   __// ___   )(  ____ \(  ____ )
| (   ) )| (    \/| (   ) || (    \/| (   ) ||  \  ( |   ) (   \/   )  || (    \/| (    )|
| (__/ / | (__    | (___) || |      | |   | ||   \ | |   | |       /   )| (__    | (____)|
|  __ (  |  __)   |  ___  || |      | |   | || (\ \) |   | |      /   / |  __)   |     __)
| (  \ \ | (      | (   ) || |      | |   | || | \   |   | |     /   /  | (      | (\ (   
| )___) )| (____/\| )   ( || (____/\| (___) || )  \  |___) (___ /   (_/\| (____/\| ) \ \__
|/ \___/ (_______/|/     \|(_______/(_______)|/    )_)\_______/(_______/(_______/|/   \__/
                                                                                         """ 

# globals
probes = set()
ssids = []
# todo: make this option
iface = 'wlan0mon'

# scapy setup
conf.verb = False
conf.iface = iface


def sniff_probe(pkt):
  if pkt.haslayer(Dot11ProbeReq):
    name=pkt[Dot11ProbeReq].info
    if len(name) > 0 and not name in probes:
      probes.add(name)
      mac_src=pkt[Dot11].addr2
      print "[+] new probe '%s' src: %s" % (name, mac_src)


def sniff_probes():
  sniff(prn=sniff_probe, store=False)


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
  try:
    if len(sys.argv) < 2:
      sys.exit("usage: %s <ssids>" % sys.argv[0])

    with open(sys.argv[1], "r") as ssid_file:
     for ssid in ssid_file:
       ssids.append(ssid.rstrip('\n'))

    t_probes=threading.Thread(target=sniff_probes)
    t_probes.daemon = True
    t_probes.start()
    send_beacons()

  except KeyboardInterrupt:
    print "[!] CTRL-C pressed, exiting"


if __name__ == "__main__":
  main()
