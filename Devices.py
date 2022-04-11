# User defined device parameter order, names and page assignments

# For every device, create a list DEVICE_PARAMETERS that lists all
# <p.original_name> parameter names in the order in which they should appear
# in the control surface, but using tow consecutive slots in the list for one
# device parameter: the first containing <p.original_name> and the second
# containing a user defined name for the parameter as it should appear in the
# control surface. If an <p.original_name> is not present in the lsit, it will
# not be shown in the control surface, and hence cannot be remote-controlled
#
# So, given a device 'Silly' with paramters 'LowFreqOsc', 'OscTune' and 'Vol'
# (in that order) and the list
#
# SILLY_PARAMETERS = [
#   'OscTune', 'Tune',
#   'LowFreqOsc', 'LFO'
# ]
# 
# that reverses the order of the parameters in the control surface, displays
# them as 'Tune' and 'LFO' and omits the 'Vol' parameter altogether
#
# Add an entry
# '<device.class_name>' ; DEVCIE_PARAMETERS
# to DEVICE_DICT (see the end of this file)


# TODO: Page assignments and page names

LOOPER_PARAMETERS = [
    'Device On', '',
    'Speed', '',
    'Quantization', '',
    'Song Control', '',
    'Tempo Control', '',
    'State', '',
    'Feedback', '',
    'Reverse', '',
    'Monitor', ''
]

ULTRA_ANALOG_PARAMETERS = []

DEVICE_DICT = {
    'Looper' : LOOPER_PARAMETERS,
    'UltraAnalog' : ULTRA_ANALOG_PARAMETERS
    }

# Return the list of parameters for a device in user defined order
def user_order(device_name, parameters):
    if device_name in DEVICE_DICT:
        parameter_info = DEVICE_DICT[device_name]
        parameter_order = [parameter_info
                           for i in range(0,len(parameter_info),2)]           # return the list of original device parameter names, i.e the ones with even index
        parameters = [x for x in parameters if x in parameter_order]          # filter out parameters not in parameter_order
        parameters.sort(key=lambda p: parameter_order.index(p.name))          # sort parameters in the order they appear in parameter_order
        return parameters

