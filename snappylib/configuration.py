#!/usr/bin/env python3.5

import configparser
import snappylib.place as place

GLOBALFILE = "/etc/snappy.conf"

class Configuration:

    # Default paths, can be overriden
    ZFS_BIN     = "/sbin/zfs"
    TARSNAP_BIN = "/usr/local/bin/tarsnap"

    def __init__(self):
        self.zfs_bin = Configuration.ZFS_BIN
        self.zfs_extra_args = []
        self.tarsnap_bin = Configuration.TARSNAP_BIN
        self.tarsnap_extra_args = []
        self._placelist = [ ]
        self.places = { }
        self.paths = { }

# Since it only really makes sense to have one configuration at a time, access
# it globally through this variable
# NOTE - this needs to be initialzed as a mutable container, rather than a
# placeholder (eg. None) and then reassigned - the latter breaks 'from x import y'
config = Configuration()

def loadINI(filename = "snappy.ini"):
    global config
    ini = configparser.ConfigParser()
    ini.read(filename)
    for name in ini.sections():
        section = ini[name]
        if name == "global":
            config.zfs_bin = section.get("zfs_bin", Configuration.ZFS_BIN)
            config.tarsnap_bin = section.get("tarsnap_bin", Configuration.TARSNAP_BIN)
            config.zfs_extra_args = section.get("zfs_extra_args","").split()
            config.tarsnap_extra_args = section.get("tarsnap_extra_args","").split()
        else:
            where = place.Place(name,section.get("path"))
            config._placelist.append(where)
            config.places[where.name] = where
            config.paths[where.path] = where
