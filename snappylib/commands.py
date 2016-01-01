#!/usr/bin/env python3

import arrow

import snappylib.util as util
from snappylib.snapshot import Snapshot, snapshots
from snappylib.place import Place
import snappylib.zfs as zfs
import snappylib.tarsnap as tarsnap

def list():
    util.loadSnapshots()
    for name, place in sorted(Place._places.items()):
        print("***** %s (%s)" % (name,place.path()))
        Snapshot.printHeader()
        for stamp in sorted(snapshots[name].keys(),key = lambda i: int(i)):
            snapshots[name][stamp].printListing()

def nuke():
    util.loadSnapshots()
    place = util.getPlace()
    snap = util.getSnap(place)
    if snap.hasTarsnap():
        tarsnap.deleteSnap(snap)
    if snap.hasZFS():
        zfs.deleteSnap(snap)

def snapZFS():
    place = util.getPlace()
    zfs.createSnapshot(place,arrow.now().timestamp)

def snapTS(place = None):
    place = util.getPlace()
    tarsnap.createSnapshot(place,arrow.now().timestamp)

def snapBoth():
    place = util.getPlace()
    now = arrow.now().timestamp
    zfs.createSnapshot(place,now)
    tarsnap.createSnapshot(place,now)

def check():
    util.check()
