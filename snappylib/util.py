#!/usr/bin/env/python3

import sys
from snappylib.snapshot import snapshots
from snappylib.place import Place

def getPlace():
    # XXX: Return actual object, support more than one
    if len(sys.argv) < 1:
      sys.exit("ERROR: place requrired")

    place = sys.argv.pop(0)
    if Place.hasName(place):
        return place
    else:
        sys.exit("ERROR: Specified nonexistent place {}".format(place))

def getSnap(place):
    if not place in snapshots:
        sys.exit("ERROR: Specified nonexistent place {}".format(place))
    if len(sys.argv) < 1:
        sys.exit("ERROR: snapshot ID requrired")
    snap = sys.argv.pop(0)
    if not snap in snapshots[place]:
        sys.exit("ERROR: Specified nonexistent snapshot {:d}".format(snap))
    return snapshots[place][snap]

