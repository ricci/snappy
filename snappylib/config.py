#!/usr/bin/env python3

import configparser
import snappylib.place as Place

# Since it only really makes sense to have one configuration at a time, access
# it globally through this variable
world = None

class Configuration:

    # Default paths, can be overriden
    ZFS_BIN     = "/sbin/zfs"
    TARSNAP_BIN = "/usr/local/bin/tarsnap"

    def __init__(self):
        self.zfs_bin = Configuration.ZFS_BIN
        self.zfs_extra_args = []
        self.tarsnap_bin = Configuration.TARSNAP_BIN
        self.tarsnap_extra_args = []
        self.places = []

def loadINI(filename = "snappy.ini"):
    global world
    world = Configuration()
    ini = configparser.ConfigParser()
    ini.read(filename)
    for name in ini.sections():
        section = ini[name]
        if name == "global":
            world.zfs_bin = section.get("zfs_bin", Configuration.ZFS_BIN)
            world.tarsnap_bin = section.get("tarsnap_bin", Configuration.TARSNAP_BIN)
            world.zfs_extra_args = section.get("zfs_extra_args","").split()
            world.tarsnap_extra_args = section.get("tarsnap_extra_args","").split()
        else:
            place = Place(name,section.get("path"))
            world.places.append(place)
