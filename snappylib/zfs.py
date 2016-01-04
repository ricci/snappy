#!/usr/bin/env python3

from subprocess import check_output

from snappylib.place import Place
from snappylib.snapshot import Snapshot
import snappylib.config as config

zfsmap = { }
_initialized = False

def initCache():
    global _initialized
    if _initialized:
        return None

    zfsout = check_output([config.world.zfs_bin,"list","-Hp"])
    for line in iter(zfsout.splitlines()):
        arr = line.decode('utf-8').split()
        path, dataset = arr[4],arr[0]
        zfsmap[path] = dataset
        zfsmap[dataset] = path
        if Place.hasPath(path):
            zfsmap[Place.byPath(path).name()] = dataset

    zfsout = check_output([config.world.zfs_bin,"list","-Hp","-t","snap"])
    for line in iter(zfsout.splitlines()):
        arr = line.decode('utf-8').split()
        snapname = arr[0]
        dataset,snap = snapname.split('@')
        if Snapshot.isSnappyZFS(snap) and dataset in zfsmap and Place.hasPath(zfsmap[dataset]):
            newsnapshot = Snapshot.factory(Place.byPath(zfsmap[dataset]).name(), Snapshot.isSnappyZFS(snap).group(1))
            newsnapshot.setZFS(snapname)

    _initialized = True

def deleteSnap(snap):
    print("deleteZFS: %s" % snap._zfs)
    check_output([config.world.zfs_bin, "destroy", "-v", snap._zfs])

def createSnapshot(place,stamp):
    initCache()

    zfssnapname = "snappy-%s" % stamp 
    zfsfullsnapname = "%s@%s" % (zfsmap[place.name()],zfssnapname)
    print("snapZFS: %s" % zfsfullsnapname)
    check_output([config.world.zfs_bin, "snapshot", zfsfullsnapname])
    # Place this in the global list in case tarsnap is going to want it
    newsnapshot = Snapshot.factory(place,stamp)
    newsnapshot.setZFS(zfsfullsnapname)

def pathForSnapshot(snap):
    dataset,snapname = snap._zfs.split('@')
    path = "{}/.zfs/snapshot/{}".format(zfsmap[dataset],snapname)
    print("pathForSnapshot {} {}".format(snapname,path))
    return path
