#!/usr/bin/env/python3

import sys
from snappylib.snapshot import snapshots
from snappylib.place import Place
import snappylib.zfs as zfs
import snappylib.tarsnap as tarsnap

def getPlace():
    if len(sys.argv) < 1:
      sys.exit("ERROR: place requrired")

    place = sys.argv.pop(0)
    if Place.hasName(place):
        return Place.byName(place)
    else:
        sys.exit("ERROR: Specified nonexistent place {}".format(place))

def getSnap(place):
    loadSnapshots()
    if not place.name() in snapshots:
        sys.exit("ERROR: Specified nonexistent place {}".format(place))
    if len(sys.argv) < 1:
        sys.exit("ERROR: snapshot ID requrired")
    snap = sys.argv.pop(0)
    if not snap in snapshots[place.name()]:
        sys.exit("ERROR: Specified nonexistent snapshot {:d}".format(snap))
    return snapshots[place.name()][snap]

def loadSnapshots():
    zfs.initCache()
    tarsnap.initCache()

def check():
    def startCheck(text):
        print("### Checking {:s} ...".format(text))
    def passCheck():
        print("    passed")
    def skipCheck(text):
        print("    skipped ({:s})".format(text))
    def failCheck(text,output):
        print("    failed: {:s}".format(text))
        if output:
            print("----------------------------------------------------------------------")
            print(output)
            print("----------------------------------------------------------------------")
    """
    Run a little test to see whether everything appears to be configured properly
    """

    startCheck("configuration file")
    skipCheck("not implemented")
