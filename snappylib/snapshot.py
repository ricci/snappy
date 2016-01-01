#!/usr/bin/env python3

import re
from subprocess import check_output
import arrow

### XXX I think these are more properly handled in a top level __init__()?
### ... actually I think I need to figure out something signficantly different

snapshots = { }

class Snapshot:
    def isSnappyZFS(snap):
        return re.match(r"snappy-(\d+)",snap)

    def isSnappyTS(snap):
        return re.match(r"snappy-(\w+)-(\d+)",snap)

    def __init__(self,place,stamp):
        self._place = place
        self._stamp = int(stamp)
        self._zfs = None
        self._tarsnap = None
        if not place in snapshots:
            snapshots[place] = { }
        snapshots[place][stamp] = self
        
    def hasZFS(self):
        return (self._zfs is not None)

    def setZFS(self,zfsname):
        self._zfs = zfsname

    def setTarsnap(self, tarsnapname):
        self._tarsnap = tarsnapname

    def hasTarsnap(self):
        return (self._tarsnap is not None)

    def printHeader():
        print("{:10}   {:<20s}   {:5}   {:5}".format("ID","When","ZFS","TS"))

    def printListing(self):
        print("{:10}   {:<20s}   {!r:5}   {!r:5}".format(self._stamp,arrow.get(self._stamp).humanize(), self.hasZFS(), self.hasTarsnap()))

    def factory(place,stamp):
        if place in snapshots and stamp in snapshots[place]:
            return snapshots[place][stamp]
        else:
            return Snapshot(place,stamp)

