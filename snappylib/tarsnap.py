#!/usr/bin/env/python3

from snappylib.snapshot import Snapshot, exists, snapshots
from snappylib.place import Place
import snappylib.zfs as zfs
from subprocess import check_output

# XXX: This stuff belongs in config files
TARSNAP_BIN  = "/usr/local/bin/tarsnap"
TARSNAP_ARGS = ["--keyfile", "/home/ricci/tarsnap-test/hactar-test.key", "--cachedir", "/home/ricci/tarsnap-test/.cache"]

__INITIALIZED__ = False

def initCache():
    global __INITIALIZED__
    if __INITIALIZED__:
        return None

    tsout = check_output([TARSNAP_BIN] +  TARSNAP_ARGS + ["--list-archives"])
    for line in iter(tsout.splitlines()):
        line = line.decode('utf-8')
        if Snapshot.isSnappyTS(line):
            groups = Snapshot.isSnappyTS(line)
            place = groups.group(1)
            stamp = groups.group(2)
            newsnapshot = Snapshot.factory(place,stamp)
            newsnapshot.setTarsnap(line.rstrip())

    __INITIALIZED__ = True

def deleteSnap(snap):
    print("deleteTS: %s" % snap._tarsnap)
    check_output([TARSNAP_BIN] + TARSNAP_ARGS + ["-d","-f",snap._tarsnap])

def createSnapshot(place, stamp):
    initCache()
    # Force ZFS cache - probably has already been initialized, but be safe
    zfs.initCache()

    if not exists(place, stamp) or not snapshots[place][stamp].hasZFS():
        sys.exit("ERROR: Trying to create tarsnap snapshot but no ZFS snap")

    tssnapname = "snappy-%s-%s" % (place, stamp)
    print("snapTS: %s" % tssnapname)
    check_output([TARSNAP_BIN] + TARSNAP_ARGS + ["-c","-f",tssnapname,Place.byName(place).path()])
