
import os
import subprocess
import time

def _check_root():
    if not os.geteuid() == 0:
      raise WifiInterfaceError("must be executed as root")      


class WifiInterfaceError(Exception):
   
  def __init__(self, message):
    self.message = message


class WifiInterface:
  
  def __init__(self, iface):
    self.iface = iface

  def set_monitor(self):
    _check_root()
    self._set_mode("monitor")    
        
  def set_channel(self, ch):
    _check_root()
    subprocess.check_call("ip link set %s down" % self.iface, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #subprocess.check_call("iwconfig %s channel %d" % (self.iface, ch), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.check_call("ip link set %s up" % self.iface, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
  def set_managed(self):
    _check_root()
    self._set_mode("managed")

  def _set_mode(self, mode):
    _check_root()
    subprocess.check_call("ip link set %s down" % self.iface, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #subprocess.check_call("iwconfig %s mode %s" % (self.iface, mode), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.check_call("iw dev %s set type %s" % (self.iface, mode), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.check_call("ip link set %s up" % self.iface, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

