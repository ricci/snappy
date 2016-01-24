#!/usr/bin/env/python3.5

import subprocess
import signal
import os

import arrow

from snappylib.snapshot import Snapshot, exists, snapshots
import snappylib.zfs as zfs
from snappylib.configuration import config

import sys

class CheapoCompletedProcess:
    def __init__(self):
        self.returncode = None
        self.stdout = None
        self.stderr = None

def runTarsnap(args, timeout = None):
    command = [config.tarsnap_bin] + config.tarsnap_extra_args + args
    proc = subprocess.Popen(command,
                stdout = subprocess.PIPE, stderr = subprocess.PIPE,
                stdin = subprocess.DEVNULL, universal_newlines = True)
    result = CheapoCompletedProcess()
    try:
        result.stdout, result.stderr = proc.communicate(timeout = timeout)
        result.returncode = proc.wait()
        if result.returncode:
            sys.exit("Error running tarsnap:\nCommand: {}\nSTDOUT:\n{}\nSTDERR:\n{}\n".format(" ".join(command),result.stdout,result.stderr))
        return result
    except subprocess.TimeoutExpired:
        print("Tarsnap timed out, sending SIGQUIT...")
        proc.send_signal(signal.SIGQUIT)
        result.stdout, result.stderr = proc.communicate()
        result.returncode = proc.wait()
        print("Tarsnap finished")
        if result.returncode:
            sys.exit("Error running tarsnap:\nCommand: {}\nSTDOUT:\n{}\nSTDERR:\n{}\n".format(" ".join(command),result.stdout,result.stderr))
        return result

_initialized = False

CACHE_FILE="/tmp/snappy.tarsnap.cache"

cache = []
def readCache():
    global cache
    if os.path.isfile(CACHE_FILE):
        cache = map(str.rstrip,open(CACHE_FILE).readlines())

def writeCache():
    global cache
    try:
        f = open(CACHE_FILE,"w")
        f.writelines(map(lambda x: x + "\n",cache))
        f.close()
    except IOError:
        # just do nothing - I think in the future, we will
        # do something clever that tells other users they should consider the
        # contents of the file to be invalid
        pass

def addToCache(entry):
    global cache
    cache.append(entry)
    writeCache()

def removeFromCache(entry):
    global cache
    cache.remove(entry)
    writeCache()

def initCache():
    global _initialized
    global cache
    if _initialized:
        return None

    if os.path.isfile(CACHE_FILE):
        readCache()
    else:
        tsout = runTarsnap(["--list-archives"])
        cache = tsout.stdout.splitlines()

    for line in cache:
        if Snapshot.isSnappyTS(line):
            groups = Snapshot.isSnappyTS(line)
            place = groups.group(1)
            stamp = groups.group(2)
            newsnapshot = Snapshot.factory(place,stamp)
            newsnapshot.setTarsnap(line.rstrip())
    writeCache()

    _initialized = True

def deleteSnap(snap):
    if snap._tarsnap:
        print("deleteTS: %s" % snap._tarsnap)
        runTarsnap(["-d","-f",snap._tarsnap])
        removeFromCache(snap._tarsnap)

    for partial in snap._tarsnap_partials + snap._tarsnap_intermediates:
        print("Cleaning up %s" % partial)
        runTarsnap(["-d","-f",partial])
        removeFromCache(partial)

def createSnapshot(place, stamp, bwlimit = None, timelimit = None):
    initCache()
    # Force ZFS cache - probably has already been initialized, but be safe
    zfs.initCache()

    if not exists(place.name, stamp) or not snapshots[place.name][stamp].hasZFS() == Snapshot.Status.complete:
        sys.exit("ERROR: Trying to create tarsnap snapshot but no ZFS snap ({},{})".format(place,stamp,))

    extraArgs = [ ]
    if bwlimit:
        extraArgs.extend(["--maxbw",str(bwlimit)])

    snap = snapshots[place.name][stamp]

    path = zfs.pathForSnapshot(snap)
    now = arrow.now().timestamp

    intermediateName = "snappy-%s-%s-intermediate-%s" % (place.name, stamp, now)
    print("snapTS: %s" % intermediateName)
    result = runTarsnap(extraArgs + ["-c","-f",intermediateName,path], timeout = timelimit)
    addToCache(intermediateName)

    tssnapname = "snappy-%s-%s" % (place.name, stamp)
    print("snapTS: %s" % tssnapname)
    runTarsnap(["-c","-f",tssnapname,path], timeout = timelimit)
    addToCache(tssnapname)

    for partial in [intermediateName] + snap._tarsnap_partials + snap._tarsnap_intermediates:
        print("Cleaning up %s" % partial)
        runTarsnap(["-d","-f",partial])
        removeFromCache(partial)

