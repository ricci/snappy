#!/usr/bin/env python3.5

from enum import Enum
import re
import hashlib
from subprocess import check_output

import arrow

from snappylib.place import Place

### XXX I think these are more properly handled in a top level __init__()?
### ... actually I think I need to figure out something signficantly different

snapshots = { }
idmap = { }

def exists(place,snap):
    return place in snapshots and snap in snapshots[place]

class Snapshot:
    class Status(Enum):
        none = 0
        complete = 1
        partial = 2

    def statusStr(status):
        if status == Snapshot.Status.none:
            return "No"
        elif status == Snapshot.Status.complete:
            return "Yes"
        else:
            return "Part"
            

    HASH = hashlib.sha256
    HASH_LEN = 4

    def isSnappyZFS(snap):
        return re.match(r"snappy-(\d+)",snap)

    #def isSnappyTS(snap):
    #    return re.match(r"snappy-(\w+)-(\d+)$",snap)

    #def isSnappyTSIntermediate(snap):
    #    return re.match(r"snappy-(\w+)-(\d+)-intermediate-(\d+)$",snap)

    def isSnappyTS(snap):
        return re.match(r"snappy-(\w+)-(\d+)(-intermediate-(\d+))?(\.part)?$",snap)

    def __init__(self,place,stamp):
        self._place = place
        self._stamp = int(stamp)
        self._zfs = None
        self._tarsnap = None
        self._tarsnap_partials = []
        self._tarsnap_intermediates = []
        if not place in snapshots:
            snapshots[place] = { }
        snapshots[place][stamp] = self
        
    def hasZFS(self):
        if self._zfs is not None:
            return Snapshot.Status.complete
        else:
            return Snapshot.Status.none

    def setZFS(self,zfsname):
        self._zfs = zfsname

    def setTarsnap(self, tarsnapname):
        groups = Snapshot.isSnappyTS(tarsnapname)
        if groups.group(5):
            self._tarsnap_partials.append(tarsnapname)
        elif groups.group(4):
            self._tarsnap_intermediates.append(tarsnapname)
        else:
            self._tarsnap = tarsnapname

    def hasTarsnap(self):
        if self._tarsnap:
            return Snapshot.Status.complete
        elif self._tarsnap_partials or self._tarsnap_intermediates:
            return Snapshot.Status.partial
        else:
            return Snapshot.Status.none

    def printHeader():
        print("{:5}   {:10}   {:<20s}   {:5}   {:5}".format("ID","Stamp","When","ZFS","TS"))

    def printListing(self):
        #print("{:10}   {:<20s}   {!r:5}   {!r:5}".format(self._stamp,arrow.get(self._stamp).humanize(), self.hasZFS(), self.hasTarsnap()))
        print("{:5}   {:10}   {:<20s}   {:5}   {:5}".format(self.shortID(),self._stamp,arrow.get(self._stamp).humanize(), Snapshot.statusStr(self.hasZFS()), Snapshot.statusStr(self.hasTarsnap())))

    def factory(place,stamp):
        if isinstance(place,Place):
            placename = place.name
        else:
            placename = place
        if place in snapshots and stamp in snapshots[placename]:
            return snapshots[placename][stamp]
        else:
            newsnap = Snapshot(placename,stamp)
            if newsnap.shortID() in idmap:
                sys.exit("Internal error, ID collision")
            idmap[newsnap.shortID()] = newsnap
            return newsnap

    def shortID(self):
        digest = Snapshot.HASH(self._place.encode('utf-8') + str(self._stamp).encode('utf-8')).hexdigest()
        return "#" + digest[0:Snapshot.HASH_LEN]
        

