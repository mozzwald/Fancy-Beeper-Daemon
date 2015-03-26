#!/usr/bin/python -u

import sys, os
from daemonize import become_daemon

SOUNDFILE = sys.argv[1]
APLAY = '/usr/bin/aplay'
PID = '/var/run/beepd.pid'

rc = become_daemon()
try:
    file(PID, 'w').write(str(rc))
except IOError:
    sys.stderr.write("Can't write PID file.\n")
try:
    beepdev = open("/dev/beep")
except IOError:
    sys.stderr.write("Can't open beep device.\n")

try:
    while 1:
        if beepdev.read(1):
            rc = os.fork()
            if not rc:
                os.execl(APLAY, APLAY, "-N", SOUNDFILE)
        else:
            continue
except:
    beepdev.close()
    sys.stderr.write("Exiting.\n")
    sys.exit(0)


