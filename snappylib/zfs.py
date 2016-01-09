#!/usr/bin/env python3.5

import subprocess
import sys
from snappylib.snapshot import Snapshot
from snappylib.configuration import config

zfsmap = { }
_initialized = False

def runZFS(args):
    command = [config.zfs_bin] + config.zfs_extra_args + args
    result = subprocess.run(command,
                stdout = subprocess.PIPE, stderr = subprocess.PIPE,
                stdin = subprocess.DEVNULL, universal_newlines = True)
    try:
        result.check_returncode()
        return result
    except subprocess.CalledProcessError as e:
        sys.exit("Error running ZFS:\nCommand: {}\nSTDOUT:\n{}\nSTDERR:\n{}\n".format(" ".join(command),result.stdout,result.stderr))

def initCache():
    global _initialized
    if _initialized:
        return None

    zfsreturn = runZFS(["list","-Hp","-o","name,mountpoint,usedbydataset,usedbysnapshots"])
    for line in iter(zfsreturn.stdout.splitlines()):
        arr = line.split()
        dataset, path, data_used, snap_used = arr
        zfsmap[path] = dataset
        zfsmap[dataset] = path
        if path in config.paths:
            place = config.paths[path]
            zfsmap[place.name] = dataset
            place.data_used = data_used
            place.snap_used = snap_used

    zfsreturn = runZFS(["list","-Hp","-t","snap"])
    for line in iter(zfsreturn.stdout.splitlines()):
        arr = line.split()
        snapname = arr[0]
        dataset,snap = snapname.split('@')
        if Snapshot.isSnappyZFS(snap) and dataset in zfsmap and zfsmap[dataset] in config.paths:
            newsnapshot = Snapshot.factory(config.paths[zfsmap[dataset]].name, Snapshot.isSnappyZFS(snap).group(1))
            newsnapshot.setZFS(snapname)

    _initialized = True

def deleteSnap(snap):
    print("deleteZFS: %s" % snap._zfs)
    runZFS(["destroy", "-v", snap._zfs])

def createSnapshot(place,stamp):
    initCache()

    zfssnapname = "snappy-%s" % stamp 
    zfsfullsnapname = "%s@%s" % (zfsmap[place.name],zfssnapname)
    print("snapZFS: %s" % zfsfullsnapname)
    runZFS(["snapshot", zfsfullsnapname])
    # Place this in the global list in case tarsnap is going to want it
    newsnapshot = Snapshot.factory(place,stamp)
    newsnapshot.setZFS(zfsfullsnapname)

def pathForSnapshot(snap):
    dataset,snapname = snap._zfs.split('@')
    path = "{}/.zfs/snapshot/{}".format(zfsmap[dataset],snapname)
    print("pathForSnapshot {} {}".format(snapname,path))
    return path

def checkForRoot(path):
    initCache()
    return path in zfsmap
