#!/usr/bin/env/python3

from snappylib.snapshot import Snapshot, exists, snapshots
import snappylib.zfs as zfs
from subprocess import check_output
from snappylib.configuration import config

import sys

_initialized = False

def initCache():
    global _initialized
    if _initialized:
        return None

    tsout = check_output([config.tarsnap_bin] + 
            config.tarsnap_extra_args + ["--list-archives"])
    for line in iter(tsout.splitlines()):
        line = line.decode('utf-8')
        if Snapshot.isSnappyTS(line):
            groups = Snapshot.isSnappyTS(line)
            place = groups.group(1)
            stamp = groups.group(2)
            newsnapshot = Snapshot.factory(place,stamp)
            newsnapshot.setTarsnap(line.rstrip())

    _initialized = True

def deleteSnap(snap):
    print("deleteTS: %s" % snap._tarsnap)
    check_output([config.tarsnap_bin] + config.tarsnap_extra_args + ["-d","-f",snap._tarsnap])

def createSnapshot(place, stamp):
    initCache()
    # Force ZFS cache - probably has already been initialized, but be safe
    zfs.initCache()

    if not exists(place.name, stamp) or not snapshots[place.name][stamp].hasZFS():
        sys.exit("ERROR: Trying to create tarsnap snapshot but no ZFS snap ({},{})".format(place,stamp,))

    tssnapname = "snappy-%s-%s" % (place.name, stamp)
    print("snapTS: %s" % tssnapname)
    path = zfs.pathForSnapshot(snapshots[place.name][stamp])
    check_output([config.tarsnap_bin] + config.tarsnap_extra_args + ["-c","-f",tssnapname,path])
