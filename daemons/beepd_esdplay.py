#!/usr/bin/python -u

import sys, os

SOUNDFILE = sys.argv[1]
ESDCAT = '/usr/bin/esdcat'

beepdev = open("/dev/beep")
dspdev = os.popen(ESDCAT, 'w')
sample = open(SOUNDFILE, 'r').read()

try:
    while 1:
        if beepdev.read(1):
            dspdev.write(sample)
        else:
            continue
except:
    beepdev.close()
    dspdev.close()
    sys.exit(0)


