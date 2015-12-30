# snappy

snappy is a little tool for managing backups using zfs and tarsnap. It's built
around snapshots.

The basic idea behind snappy is:

 * You have a live filesysem stored on a ZFS pool
 * You have some set of snapshots of that filesystem (these snapshots
   are managed by snappy)
 * Some of these snapshots are backed up remotely to tarsnap

Snappy's job is to manage the zfs snapshots (via cron, run by hand, etc.) and
their backups.
