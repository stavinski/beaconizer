# Beaconizer

A tool written in python that sends multiple wifi beacon frames in order to try and elicit a response from a
wifi client, assuming they already have the SSID in the list of remembered access points.

## Gathering SSIDs

1. Wardriving around common hotspot locations to gather a list of open wifi access points
2. Use the work of others at https://www.wigle.net/ to gather a list around your target location

## Usage

```sh
usage: beaconizer.py [-h] [-i IFACE] [-c CHANNEL] [-o OUTFILE] ssids

positional arguments:
  ssids                 file with list of SSIDs to use, use - for STDIN

optional arguments:
  -h, --help            show this help message and exit
  -i IFACE, --iface IFACE
                        wifi iface to use
  -c CHANNEL, --channel CHANNEL
                        channel to use
  -o OUTFILE, --outfile OUTFILE
                        file to write output to, uses STDOUT by default
```

# Python3

I have created a separate python3 branch with changes to make it compatible