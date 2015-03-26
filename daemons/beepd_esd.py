#!/usr/bin/python -u

import esd, sys, sndhdr, wave, sunau

try:
    SOUNDFILE = sys.argv[1]
except:
    SOUNDFILE = "/usr/local/share/sounds/wav/ds9/intercom.wav"

class MyError(Exception):
    pass

try:
    rate, channels, bits, data = 0, 0, 0, 0
    if SOUNDFILE[-3:] == 'wav' or SOUNDFILE[-3] == 'WAV':
        wav = wave.open(SOUNDFILE, 'r')
        rate = wav.getframerate()
        channels = wav.getnchannels()
        width = wav.getsampwidth()
        if wav.comptype() != 'NONE':
            raise MyError, "Unsupported wave compression type!"
        data = wav.readframes(wav.getnframes())
        wav.close()
    elif SOUNDFILE[-2:] == 'au' or SOUNDFILE[-2:] == 'AU':
        au = sunau.open(SOUNDFILE, 'r')
        rate = au.getframerate()
        channels = au.getnchannels()
        width = au.getsampwidth()
        data = au.readframes(au.getnframes())
        au.close()
    else:
        raise "catchme"
except (MyError, wave.Error, sunau.Error, IOError), what:
    sys.stderr.write("%s: %s\n" % (sys.exc_info()[0],  what))
    sys.exit(0)
except:
    soundinfo = sndhdr.what(SOUNDFILE)
    if soundinfo:
        type, rate, channels, frames, bits = soundinfo
        width = bits/8

if channels == 1:
    channel_format = esd.ESD_MONO
elif channels == 2:
    channel_format = esd.ESD_STEREO
else: channel_format = 0

if width == 1:
    width_format = esd.ESD_BITS8
elif width == 2:
    width_format = esd.ESD_BITS16
else: width_format = 0

if not rate:
    rate = esd.ESD_DEFAULT_RATE

# define format and rate info for all subsequent calls
fmt = esd.ESD_PLAY | channel_format | width_format


# make a sample of the sound.
if data:
    sample = esd.Sample(fmt, rate, data)
    del data
else:
    sample = esd.Sample(fmt, rate, open(SOUNDFILE).read())

# connect to daemon
s = esd.ServerSession()

# cache sound in server
sampleId = s.cacheSample(sample, 'system beep')
del sample

beepdev = open("/dev/beep")
try:
    while 1:
        if beepdev.read(1):
            s.playSample(sampleId)
        else:
            continue
except:
    s.freeSample(sampleId)
    del s
    beepdev.close()
    sys.exit(0)


