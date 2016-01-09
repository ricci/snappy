#!/usr/bin/env python3.5

import sys
import re

import arrow

import snappylib.util as util
from snappylib.snapshot import Snapshot, snapshots
import snappylib.zfs as zfs
import snappylib.tarsnap as tarsnap
from snappylib.configuration import config

class Command:
    ARG_PLACE = "place"
    ARG_SNAP = "snap"
    ARG_ID = "#id"

    def __init__(self, name, args, descr, function):
        self._name = name
        self._args = args
        self._descr = descr
        self._function = function

    def call(self):
        return self._function()

    def describe(self):
        if self._args:
            argstring = " ".join(map(lambda s: "<" + s + ">",self._args))
        else:
            argstring = ""
        return "  {:<7s} {:<14s} {}".format(self._name,argstring,self._descr)

all = [ ]
byname = { }

def newCommand(name, args, descr, function):
    cmd = Command(name, args, descr, function)
    all.append(cmd)
    byname[name] = cmd
    return cmd

def usagemsg():
    print("Usage: snappy <command> [args]")
    for cmd in all:
        print(cmd.describe())

usage = newCommand("help", None, "This usage message", usagemsg)

def check():
    util.check()

newCommand("check", None, "Perform some configuration checks", check)

def list():
    util.loadSnapshots()
    for name, place in sorted(config.places.items()):
        print("***** %s (%s) %s / %s" % (name,place.path,util.readableBytes(place.data_used),util.readableBytes(place.snap_used)))
        Snapshot.printHeader()
        for stamp in sorted(snapshots[name].keys(),key = lambda i: int(i)):
            snapshots[name][stamp].printListing()

newCommand("list", None, "List all snapshots", list)

def summary():
    util.loadSnapshots()
    for name, place in sorted(config.places.items()):
        count = len(snapshots[name])
        recent = sorted(snapshots[name].keys(),key = lambda i: int(i)).pop()
        print("{:<12s}   {:>5d} snapshots   {:<20s}".format(name,count,arrow.get(recent).humanize()))

newCommand("summary", None, "Give a summary of snapshots", summary)

def snapBoth():
    place = util.getPlace()
    now = arrow.now().timestamp
    zfs.createSnapshot(place,now)
    tarsnap.createSnapshot(place,now)

newCommand("snap", [ Command.ARG_PLACE ], "Create a new snapshot (both ZFS and tarsnap)",
        snapBoth)

def snapZFS():
    place = util.getPlace()
    zfs.createSnapshot(place,arrow.now().timestamp)

newCommand("snapzfs", [ Command.ARG_PLACE ], "Create a new ZFS snapshot",
        snapZFS)

def snapTS():
    snap = util.getSnapshot()
    if len(sys.argv) > 0:
        limittext = sys.argv.pop(0)
        match = re.match("(\d+)([KMG])",limittext)
        if not match:
            sys.exit("Bandwidth limit must be <INT>[K|M|G]")
        else:
            if match.group(2) == "K":
                bwlimit = int(match.group(1)) * 1000
            elif match.group(2) == "M":
                bwlimit = int(match.group(1)) * 1000000
            elif match.group(3) == "G":
                bwlimit = int(match.group(1)) * 1000000000
        print("Will shutdown tarsnap after {} bytes".format(bwlimit))
    else:
        bwlimit = None

    # XXX: Crappy to get a snap object and pull out the stamp
    tarsnap.createSnapshot(config.places[snap._place],str(snap._stamp),bwlimit)

newCommand("snapts", [ Command.ARG_ID ], "Create a tarsnap snapshot from an existing ZFS snap",
        snapTS)

def rmTS():
    util.loadSnapshots()
    snap = util.getSnapshot()
    if snap.hasTarsnap() == Snapshot.Status.complete or snap.hasTarsnap() == Snapshot.Status.partial:
        tarsnap.deleteSnap(snap)

newCommand("rmts", [ Command.ARG_ID ], "Remove the tarsnap half of an existing snap",
        rmTS)

def nuke():
    util.loadSnapshots()
    snap = util.getSnapshot()
    if snap.hasTarsnap() == Snapshot.Status.complete or snap.hasTarsnap() == Snapshot.Status.partial:
        tarsnap.deleteSnap(snap)
    if snap.hasZFS() == Snapshot.Status.complete:
        zfs.deleteSnap(snap)

newCommand("nuke", [Command.ARG_ID ], "Remove snapsot", nuke)
