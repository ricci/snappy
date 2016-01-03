#!/usr/bin/env python3

from subprocess import check_output
ZFS_BIN      = "/sbin/zfs"

from snappylib.place import Place
from snappylib.snapshot import Snapshot

zfsmap = { }
__INITIALIZED__ = False

def initCache():
    global __INITIALIZED__
    if __INITIALIZED__:
        return None

    zfsout = check_output([ZFS_BIN,"list","-Hp"])
    for line in iter(zfsout.splitlines()):
        arr = line.decode('utf-8').split()
        path, dataset = arr[4],arr[0]
        zfsmap[path] = dataset
        zfsmap[dataset] = path
        if Place.hasPath(path):
            zfsmap[Place.byPath(path).name()] = dataset

    zfsout = check_output([ZFS_BIN,"list","-Hp","-t","snap"])
    for line in iter(zfsout.splitlines()):
        arr = line.decode('utf-8').split()
        snapname = arr[0]
        dataset,snap = snapname.split('@')
        if Snapshot.isSnappyZFS(snap) and dataset in zfsmap and Place.hasPath(zfsmap[dataset]):
            newsnapshot = Snapshot.factory(Place.byPath(zfsmap[dataset]).name(), Snapshot.isSnappyZFS(snap).group(1))
            newsnapshot.setZFS(snapname)

    __INITIALIZED__ = True

def deleteSnap(snap):
    print("deleteZFS: %s" % snap._zfs)
    check_output([ZFS_BIN, "destroy", "-v", snap._zfs])

def createSnapshot(place,stamp):
    initCache()

    zfssnapname = "snappy-%s" % stamp 
    zfsfullsnapname = "%s@%s" % (zfsmap[place.name()],zfssnapname)
    print("snapZFS: %s" % zfsfullsnapname)
    check_output([ZFS_BIN, "snapshot", zfsfullsnapname])
    # Place this in the global list in case tarsnap is going to want it
    newsnapshot = Snapshot.factory(place,stamp)
    newsnapshot.setZFS(zfsfullsnapname)

def pathForSnapshot(snap):
    dataset,snapname = snap._zfs.split('@')
    path = "{}/.zfs/snapshot/{}".format(zfsmap[dataset],snapname)
    print("pathForSnapshot {} {}".format(snapname,path))
    return path
