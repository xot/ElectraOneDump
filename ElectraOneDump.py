# ElectrOneDump
#
# Ableton Live MIDI Remote Script to dump an ElectraOne JSON preset for
# the currently selected device
#
# Author: Jaap-henk Hoepman (info@xot.nl)
#
# Distributed under the MIT License, see LICENSE
#

# Python imports
import os, io

# Ableton Live imports
from _Framework.ControlSurface import ControlSurface
from _Generic.util import DeviceAppointer

from .ElectraOneDumper import construct_json_patchinfo

LOCALDIR = 'src/ableton-control-scripts/ElectraOneDump/dumps'
DEBUG = True


def dump_preset(device):
    u"""Dump the parameters in the device as a ElectraOne JSON preset"""
    #
    device_name = device.class_name
    info = construct_json_patchinfo( device_name, device.parameters )
    s = info.get_patch()
    home = os.path.expanduser("~")
    path =  f'{ home }/{ LOCALDIR }'
    if not os.path.exists(path):
        path = home
#    self.log_message(f'dumping device: { device_name }.')
    fname = f'{ path }/{ device_name }.json'
    with open(fname,'w') as f:            
        f.write(s)
    fname = f'{ path }/{ device_name }.ccmap'
    with open(fname,'w') as f:
        comma = False
        f.write('{')
        for p in device.parameters:
            name = p.original_name
            cc = info.get_cc_for_parameter(name)
            if cc:
                if comma:
                    f.write(',')
                comma = True
            f.write(f"'{ name }': { cc }\n")
        f.write('}')

        
class ElectraOneDump(ControlSurface):
    u""" Script to dump the parameters of the currently selected device """

    def error(s):
        self.log_message(f'error: {s}')


    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        # TODO: check that indeed an Electra One is connected
        self.__c_instance = c_instance
        self._appointed_device = None
        # register a device appointer;  _set_appointed_device will be called when appointed device changed
        # see _Generic/util.py
        self._device_appointer = DeviceAppointer(song=self.__c_instance.song(), appointed_device_setter=self._set_appointed_device)
        self.log_message("ElectraOneDump loaded.")

    def debug(self,m):
        if DEBUG:
            self.log_message(m)

    def update_display(self):
        pass
    
    def _set_appointed_device(self, device):
        self.debug(f'ElectraOne device appointed { device.class_name }')
        if device != self._appointed_device:
            self._appointed_device = device
            if device != None:
                dump_preset(device)
