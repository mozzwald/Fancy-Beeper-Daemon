#!/usr/bin/python -u

import sys

SOUNDFILE = sys.argv[1]

# make a sample of the sound.
sample = open(SOUNDFILE).read()

beepdev = open("/dev/beep")

try:
    while 1:
        if beepdev.read(1):
            dspdev = open("/dev/dsp", "w")
            dspdev.write(sample)
            dspdev.close()
        else:
            continue
except IOError, OSError:
    continue # If we can't open the dsp device, ignore it.
except:
    beepdev.close()
    dspdev.close()
    sys.exit(0)


