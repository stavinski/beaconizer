
import sys
import os
import time


class WifiInterfaceError(Exception):
   
  def __init__(self, message):
    self.message = message

def _check_root():
    if not os.geteuid() == 0:
      raise WifiInterfaceError("must be executed as root")      
  

class WifiInterface:
  
  def __init__(self, iface):
    self.iface = iface

  def set_monitor(self):
    _check_root()
    self._set_mode("monitor")    
        
  def set_channel(self, ch):
    _check_root()
    os.system("ifconfig %s down" % self.iface)
    os.system("iwconfig %s channel %d" % (self.iface, ch))
    os.system("ifconfig %s up" % self.iface)
    
  def set_managed(self):
    _check_root()
    self._set_mode("managed")

  def _set_mode(self, mode):
    _check_root()
    os.system("ifconfig %s down" % self.iface)
    os.system("iwconfig %s mode %s" % (self.iface, mode))
    os.system("ifconfig %s up" % self.iface)
