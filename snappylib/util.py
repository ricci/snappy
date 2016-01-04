#!/usr/bin/env/python3

import sys
import os.path
import configparser
import snappylib.snapshot as snapshot
import snappylib.zfs as zfs
import snappylib.tarsnap as tarsnap
from snappylib.configuration import config
import snappylib.configuration as configuration

def getPlace():
    if len(sys.argv) < 1:
      sys.exit("ERROR: place requrired")

    name = sys.argv.pop(0)
    if name in config.places:
        return config.places[name]
    else:
        sys.exit("ERROR: Specified nonexistent place {}".format(name))

def getSnap(place):
    loadSnapshots()
    if not place.name in snapshot.snapshots:
        sys.exit("ERROR: Specified nonexistent place {}".format(place.name))
    if len(sys.argv) < 1:
        sys.exit("ERROR: snapshot ID requrired")
    snap = sys.argv.pop(0)
    if not snap in snapshot.snapshots[place.name]:
        sys.exit("ERROR: Specified nonexistent snapshot {:d}".format(snap))
    return snapshot.snapshots[place.name][snap]

def getSnapshot():
    """
    Get a snapshot, which can either be "place snap" or "#id"
    """
    if len(sys.argv) < 1:
        sys.exit("ERROR: snapshot ID requrired")

    loadSnapshots()

    passed = sys.argv[0]

    if passed[0:1] == "#":
        sys.argv.pop(0)
        if passed in snapshot.idmap:
            return snapshot.idmap[passed]
        else:
            sys.exit("ERROR: Specified nonexistent snapshot {}".format(passed))
    else:
        place = getPlace()
        snap = getSnap(place)
        return snap

def loadSnapshots():
    zfs.initCache()
    tarsnap.initCache()

def check():
    checkFailed = False
    def startCheck(text):
        nonlocal checkFailed
        print("### Checking {:s} ...".format(text))
        checkFailed = False
    def passCheck():
        print("    passed")
    def skipCheck(text):
        print("    skipped ({:s})".format(text))
    def failCheck(text,output = None):
        nonlocal checkFailed
        print("    failed: {:s}".format(text))
        checkFailed = True
        if output:
            print("----------------------------------------------------------------------")
            print(output)
            print("----------------------------------------------------------------------")
    """
    Run a little test to see whether everything appears to be configured properly
    """

    startCheck("whether configuration file exists") 
    # XXX Specify alternate config file
    if os.path.isfile("snappy.ini"):
        passCheck()
    else:
        failCheck("No configuration file (snappy.ini) found")

    startCheck("whether configuration file parses") 
    try:
        configuration.loadINI("snappy.ini")
    except configparser.Error as e:
        failCheck("Error parsing configuration file (snappy.ini)", str(e))
    else:
        passCheck()

    startCheck("for ZFS binary")
    if os.path.isfile(config.zfs_bin) and os.access(config.zfs_bin, os.X_OK):
        passCheck()
    else:
        failCheck("Can't find ZFS executable","""
        Can't find (or execute) the ZFS executable at {}.
        If it's installed somewhere else, set the zfs_path variable
        in the [global] section of your config file
        """.format(config.zfs_bin))

    startCheck("for tarsnap binary")
    if os.path.isfile(config.tarsnap_bin) and os.access(config.zfs_bin, os.X_OK):
        passCheck()
    else:
        failCheck("Can't find tarsnap executable","""
        Can't find (or execute) the tarsnap executable at {}.

        On FreeBSD, install it with 'pkg install tarsnap'

        If it's installed somewhere else, set the tarsnap_path variable
        in the [global] section of your config file
        """.format(config.tarsnap_bin))

    startCheck("for places to back up")
    if not config.places:
        failCheck("No places defined","""
        Your config file doesn't define anyplace to back up. Each location must
        look, at a minimum, like this:

        [place_name]
        path = /path/to/somehwere
        """)
    else:
        for name, place in config.places.items():
            if not place.path:
                failCheck("No path defined for [{}]".format(place.name))
            if not zfs.checkForRoot(place.path):
                failCheck("{} ({}) is not the root of a ZFS filesystem".format(place.path,place.name),"""
                snappy requires that each place to back up be the root of a ZFS
                filesystem. If you want to back up a smaller unit, simply create
                a new filesystem at the desired mountpoint
                """)
    if not checkFailed:
        passCheck()
