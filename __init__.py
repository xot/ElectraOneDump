#
from .ElectraOneDump import ElectraOneDump

def create_instance(c_instance):
    u""" Creates and returns the ElectraOneDump script """
    return ElectraOneDump(c_instance)
