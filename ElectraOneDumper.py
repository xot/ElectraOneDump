# ElectrOneDumper - actual dumping code
#
# Ableton Live MIDI Remote Script to dump an ElectraOne JSON preset for
# the currently selected device
#
# Author: Jaap-henk Hoepman (info@xot.nl)
#
# Distributed under the MIT License, see LICENSE
#

# Ableton Live imports
from _Framework.ControlSurface import ControlSurface

import io

# TODO: use p.name or p.original_name??

MIDI_PORT = 1
MIDI_CHANNEL = 11
DEVICE_ID = 1

# Electra One JSON file format version
VERSION = 2
# FIXME
PROJECT_ID = 'NOs0I61ql9nDebe5pE2b'

PARAMETERS_PER_PAGE = 3 * 12
CONTROLSETS_PER_PAGE = 3
SLOTS_PER_ROW = 6

COLOR = 'FFFFFF'

# bounds constants

WIDTH = 146
HEIGHT = 56
XCOORDS = [0,170,340,510,680,850]
YCOORDS = [40,128,216,304,392,480]

# maximum values in a preset

MAX_NAME_LEN =14
MAX_ID = 432
MAX_PAGE_ID = 12
MAX_OVERLAY_ID = 51

# --- MutableString---

# A mutuable string class that allows the gradual construction of long strinsg
# by appending to it.
class MutableString(io.StringIO):

    def __init__(self):
        super(MutableString, self).__init__()

    def append(self,*elements):
        for e in elements:
            self.write(str(e))

# --- PatchInfo ---

class PatchInfo ():
    # - The preset is a JSON string in Electra One format.
    #   (The current implementation assumes that all quantized parameters
    #   are 7-bit absolute CC values while all non quantized parameters are
    #   14-bit absolute values)
    # - The MIDI cc mapping data is a dictionary of Ableton Live original
    #   parameter names with their corresponding MIDI CC values in the preset.

    def __init__(self,json_patch,cc_map):
        self._json_patch = json_patch
        self._cc_map = cc_map

    # Return the MIDI CC parameter assigned to the device parameter. Return
    # None if not mapped.
    def get_cc_for_parameter(self,parameter_original_name):
        assert self._cc_map != None, 'Empty cc-map'
        if parameter_original_name in self._cc_map:
            return self._cc_map[parameter_original_name] 
        else:
            return None

    def get_patch(self):
        assert self._json_patch != None, 'Empty JSON patch'
        return self._json_patch
     
# ---

# return the MIDI CC assigned to a parameter with index i
def cc_for_idx(i):
    return i+1

# append a comma if flag; return true; use-case
# flag = false
# flag = append_comma(flag)
# to append comma's to a list
def append_comma(s,flag):
    if flag:
        s.append(',')
    return True

# check/truncate name
def check_name(name):
    # TODO log truncation
    return name[:MAX_NAME_LEN]

def check_id(id):
    assert id <= MAX_ID, f'Max number of IDs ({ MAX_ID }) exceeded.'
    return id

def check_pageid(id):
    assert id <= MAX_PAGE_ID, f'Max number of pages ({ MAX_PAGE_ID }) exceeded.'
    return id

def check_overlayid(id):
    assert id <= MAX_OVERLAY_ID, f'Max number of overlays ({ MAX_OVERLAY_ID }) exceeded.'
    return id

# ---

def append_json_pages(s,parameters) :
    s.append(',"pages":[')
    pagecount = 1 + (len(parameters) // PARAMETERS_PER_PAGE)
    flag = False
    for i in range(1,pagecount+1):
        flag = append_comma(s,flag)
        s.append( f'{{"id":{ check_pageid(i) },"name":"Page { i }"}}')
    s.append(']')

# Does the parameter have the values "Off" and "On" only
def is_on_off_parameter(p):
    if not p.is_quantized:
        return False
    values = p.value_items
    if (len(values) != 2):
        return False
    else:
        return ( (str(values[0]) == "Off") and (str(values[1]) == "On"))

# Does the parameter need an overlay to be generated (that enumerates all the
# values in the list)
def needs_overlay(p):
    return p.is_quantized and (not is_on_off_parameter(p))

def append_json_overlay_item(s,label,index,value):
    s.append( f'{{"label":"{ label }"' 
            , f',"index":{ index }'
            , f',"value":{ value }'
            ,  '}'
            )
    

def append_json_overlay_items(s,value_items):
    s.append(',"items":[')
    flag = False
    for (idx,item) in enumerate( value_items ):
        # for a list with n items, item i (staring at 0) has MIDI CC control
        # value round(i * 127/(n-1)) 
        item_cc_value = round( idx * (127 / (len(value_items)-1) ) )
        flag = append_comma(s,flag)
        append_json_overlay_item(s,item,idx,item_cc_value)
    s.append(']')

def append_json_overlay(s,idx,parameter):
    s.append(f'{{"id":{ check_overlayid(idx) }')
    append_json_overlay_items(s,parameter.value_items)
    s.append('}')

def append_json_overlays(s,parameters):
    s.append(',"overlays":[')
    overlay_idx = 1
    flag = False
    for p in parameters:
        if needs_overlay(p):
           flag = append_comma(s,flag)
           append_json_overlay(s,overlay_idx,p)
           overlay_idx = overlay_idx + 1
    s.append(']')
    
def append_json_bounds(s,idx):
    idx = idx % PARAMETERS_PER_PAGE
    # (0,0) is top left slot
    x = idx % SLOTS_PER_ROW
    y = idx // SLOTS_PER_ROW
    s.append( f',"bounds":[{ XCOORDS[x] },{ YCOORDS[y] },{ WIDTH },{ HEIGHT }]' )

# construct a toggle pad for an on/off valued list
def append_json_toggle(s,idx):
    s.append( ',"type":"pad"'
            , ',"mode":"toggle"'
            , ',"values":[{"message":{"type":"cc7"'
            ,                       ',"offValue": 0'
            ,                       ',"onValue": 127'
            ,                      f',"parameterNumber":{ cc_for_idx(idx) }'
            ,                      f',"deviceId":{ DEVICE_ID }'
            ,                       '}' 
            ,            ',"id":"value"'
            ,            '}]'
            )

def append_json_list(s,idx, overlay_idx):
    s.append( ',"type":"list"'
            ,  ',"values":[{"message":{"type":"cc7"' 
            ,                       f',"parameterNumber":{ cc_for_idx(idx+1) } '
            ,                       f',"deviceId":{ DEVICE_ID }'
            ,                        '}' 
            ,            f',"overlayId": { check_overlayid(overlay_idx) }'
            ,             ',"id":"value"'
            ,             '}]'
            )

# Return the number part in the string representation of the value of a parameter
def get_par_number_part(p,v):
    value_as_str = p.str_for_value(v)                                         # get value as a string
    (number_part,sep,rest) = value_as_str.partition(' ')                      # split ar the first space
    return number_part


# Determine whether the parameter is integer
def is_int_parameter(p):
    min_number_part = get_par_number_part(p,p.min)
    max_number_part = get_par_number_part(p,p.max)
    return min_number_part.isnumeric() and max_number_part.isnumeric() 


# TODO: add values for float parameters using
# - parameter.str_for_value()
# - parameter.min
# - parameter.max
#
def append_json_fader(s,idx, p):
    if is_int_parameter(p):
        min = get_par_number_part(p,p.min)
        max = get_par_number_part(p,p.max)
    else:
        min = 0
        max = 16383
    s.append( ',"type":"fader"'
            , ',"values":[{"message":{"type":"cc14"' 
            ,                      f',"parameterNumber":{ cc_for_idx(idx) }'
            ,                      f',"deviceId":{ DEVICE_ID }'
            ,                       ',"lsbFirst":false'
            ,                      f',"min":{ min }'
            ,                      f',"max":{ max }'
            ,                      '}'
            ,            ',"id":"value"'
            ,            '}]'
            )

# TODO: FIXME: global parameter   
overlay_idx = 0


# idx: starts at 0!
def append_json_control(s, idx, parameter):
    global overlay_idx
    page = 1 + (idx // PARAMETERS_PER_PAGE)
    controlset = 1 + ((idx % PARAMETERS_PER_PAGE) // (PARAMETERS_PER_PAGE // CONTROLSETS_PER_PAGE))
    pot = 1 + (idx % (PARAMETERS_PER_PAGE // CONTROLSETS_PER_PAGE))
    s.append( f'{{"id": { check_id(idx+1) }'
            , f',"name":"{ check_name(parameter.name) }"'
            ,  ',"visible":true' 
            , f',"color":"{ COLOR }"' 
            , f',"pageId":{ page }'
            , f',"controlSetId":{ controlset }'
            , f',"inputs":[{{"potId":{ pot },"valueId":"value"}}]'
            )
    append_json_bounds(s,idx)
    # TODO diversify:
    # - ADSRs
    # - real and integer valued faders;
    # also overlay_idx implicitly matched to parameter; dangerous
    if needs_overlay(parameter):
        append_json_list(s,idx,overlay_idx)
        overlay_idx = overlay_idx + 1
    elif is_on_off_parameter(parameter):
        append_json_toggle(s,idx)
    else:
        append_json_fader(s,idx,parameter)
    s.append('}')


        
def append_json_controls(s,parameters):
    global overlay_idx
    s.append(',"controls":[')
    overlay_idx = 1
    flag = False
    for (i,p) in enumerate(parameters):
        flag = append_comma(s,flag)
        append_json_control(s,i,p)
    s.append(']')
             
ORDER_ORIGINAL = 0
ORDER_SORTED = 1
ORDER = ORDER_ORIGINAL

# Order the parameters: original, sorted by name, or user defined
# WHEN USER DEFINED< RETRIEVE THE JSON FROM EXTERNAL STORAGE
def order_parameters(device_name, parameters):
    if (ORDER == ORDER_ORIGINAL):
        return parameters
    else: # ORDER == ORDER_SORTED
        parameters_copy = []
        for p in parameters:
            parameters_copy.append(p)
        parameters_copy.sort(key=lambda p: p.name)
        return parameters_copy

def construct_json_preset(device_name, parameters):
    u"""Construct a Electra One JSON preset for the given list of Ableton Live 
        Device/Instrument parameters. Return as string."""
    #
    s = MutableString()
    s.append( f'{{"version": { VERSION }'
            , f',"name":"{ check_name(device_name) }"'
            , f',"projectId":"{ PROJECT_ID }"'
            )
    append_json_pages(s, parameters)
    s.append( f',"devices":[{{"id":{ DEVICE_ID }'
            ,                ',"name":"Generic MIDI"'
            ,               f',"port":{ MIDI_PORT }'
            ,               f',"channel":{ MIDI_CHANNEL }'
            ,                '}]'
            )
    append_json_overlays (s, parameters)
    s.append( ',"groups":[]')
    append_json_controls (s, parameters)
    s.append( '}' )
    return s.getvalue()

def construct_patch_map(parameters):
    cc_map = {}
    for (i,p) in  enumerate(parameters):
        cc_map[p.original_name] = cc_for_idx(i)
    return cc_map

def construct_json_patchinfo(device_name, parameters):
    u"""Construct a Electra One JSON preset and a corresponding
        dictionary for the mapping to MIDI CC values for the given list of
        Ableton Live Device/Instrument parameters. Return as PatchInfo."""

    parameters = order_parameters(device_name,parameters)    
    patch_json = construct_json_preset(device_name, parameters)
    cc_map = construct_patch_map(parameters)
    return PatchInfo(patch_json,cc_map)
