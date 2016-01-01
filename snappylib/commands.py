#!/usr/bin/env python3

import arrow

import snappylib.util as util
from snappylib.snapshot import Snapshot, snapshots
from snappylib.place import Place
import snappylib.zfs as zfs
import snappylib.tarsnap as tarsnap

class Command:
    ARG_PLACE = "place"
    ARG_SNAP = "snap"

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
    for name, place in sorted(Place._places.items()):
        print("***** %s (%s)" % (name,place.path()))
        Snapshot.printHeader()
        for stamp in sorted(snapshots[name].keys(),key = lambda i: int(i)):
            snapshots[name][stamp].printListing()

newCommand("list", None, "List all snapshots", list)

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
    place = util.getPlace()
    tarsnap.createSnapshot(place,arrow.now().timestamp)

newCommand("snapts", [ Command.ARG_PLACE ], "Create a new tarsnap snapshot",
        snapTS)

def nuke():
    util.loadSnapshots()
    place = util.getPlace()
    snap = util.getSnap(place)
    if snap.hasTarsnap():
        tarsnap.deleteSnap(snap)
    if snap.hasZFS():
        zfs.deleteSnap(snap)

newCommand("nuke", [Command.ARG_PLACE, Command.ARG_SNAP ], "Remove snapsot", nuke)

