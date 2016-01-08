#!/usr/bin/env/python3.5

import subprocess

from snappylib.snapshot import Snapshot, exists, snapshots
import snappylib.zfs as zfs
from snappylib.configuration import config

import sys

def runTarsnap(args):
    command = [config.tarsnap_bin] + config.tarsnap_extra_args + args
    result = subprocess.run(command,
                stdout = subprocess.PIPE, stderr = subprocess.PIPE,
                stdin = subprocess.DEVNULL, universal_newlines = True)
    try:
        result.check_returncode()
        return result
    except subprocess.CalledProcessError as e:
        sys.exit("Error running tarsnap:\nCommand: {}\nSTDOUT:\n{}\nSTDERR:\n{}\n".format(" ".join(command),result.stdout,result.stderr))

_initialized = False

def initCache():
    global _initialized
    if _initialized:
        return None

    tsout = runTarsnap(["--list-archives"])
    for line in iter(tsout.stdout.splitlines()):
        if Snapshot.isSnappyTS(line):
            groups = Snapshot.isSnappyTS(line)
            place = groups.group(1)
            stamp = groups.group(2)
            newsnapshot = Snapshot.factory(place,stamp)
            newsnapshot.setTarsnap(line.rstrip())

    _initialized = True

def deleteSnap(snap):
    print("deleteTS: %s" % snap._tarsnap)
    runTarsnap(["-d","-f",snap._tarsnap])

def createSnapshot(place, stamp, bwlimit = None):
    initCache()
    # Force ZFS cache - probably has already been initialized, but be safe
    zfs.initCache()

    if not exists(place.name, stamp) or not snapshots[place.name][stamp].hasZFS() == Snahshot.Status.complete:
        sys.exit("ERROR: Trying to create tarsnap snapshot but no ZFS snap ({},{})".format(place,stamp,))

    extraArgs = [ ]
    if bwlimit:
        extraArgs.extend(["--maxbw",str(bwlimit)])

    tssnapname = "snappy-%s-%s" % (place.name, stamp)
    print("snapTS: %s" % tssnapname)
    path = zfs.pathForSnapshot(snapshots[place.name][stamp])
    runTarsnap(extraArgs + ["-c","-f",tssnapname,path])
