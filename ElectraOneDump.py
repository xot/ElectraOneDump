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

from .ElectraOneDumper import construct_json_preset

LOCALDIR = 'src/ableton-control-scripts/ElectraOneDump/dumps'

def dump_preset(device):
    u"""Dump the parameters in the device as a ElectraOne JSON preset"""
    #
    device_name = device.class_name
    s = construct_json_preset( device_name, device.parameters )
    home = os.path.expanduser("~")
    path =  f'{ home }/{ LOCALDIR }'
    if not os.path.exists(path):
        path = home
#    self.log_message(f'dumping device: { device_name }.')
    fname = f'{ path }/{ device_name }.json'
    with open(fname,'w') as f:            
        f.write(s)

        
class ElectraOneDump(ControlSurface):
    u""" Script to dump the parameters of the currently selected device """

    def error(s):
        self.log_message(f'error: {s}')


    def __init__(self, *a, **k):
        super(ElectraOneDump, self).__init__(*a, **k)
        self._appointed_device = None
        self.log_message("ElectraOneDump loaded.")

    def update_display(self):
        device = self.song().appointed_device
        if device != self._appointed_device:
            self._appointed_device = device
            if device != None:
                dump_preset(device)
