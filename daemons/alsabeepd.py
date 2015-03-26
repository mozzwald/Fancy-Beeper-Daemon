#!/usr/bin/env python

# written by Lars Immisch <lars@ibp.de>

# This is a custom beep daemon for the Fancy Beep Driver from
# http://www.carcosa.net/jason/software/beep/

# This beep daemon also needs pyalsaaudio from
# http://sourceforge.net/projects/pyalsaaudio

import alsaaudio
import sys
import time
import struct
import cStringIO

BEEP = '/usr/share/sounds/Pop.wav'

# this is all a bit simplified, and won't cope with any wav extensions
# or multiple data chunks, but we don't need that

WAV_FORMAT_PCM = 1
WAV_HEADER_SIZE = struct.calcsize('<4sl4s4slhhllhh4sl')


def wav_header_unpack(data):
    (riff, riffsize, wave, fmt, fmtsize, format, nchannels, framerate, 
     datarate, blockalign, bitspersample, data, datalength) \
     = struct.unpack('<4sl4s4slhhllhh4sl', data)

    if riff != 'RIFF' or fmtsize != 16 or fmt != 'fmt ' or data != 'data':
        raise ValueError, 'illegal wav header'
    
    return (format, nchannels, framerate, datarate, datalength)

def daemonize(stdout='/dev/null', stderr=None, stdin='/dev/null',
              pidfile=None):
    '''
        This forks the current process into a daemon.
        The stdin, stdout, and stderr arguments are file names that
        will be opened and used to replace the standard file descriptors
        in sys.stdin, sys.stdout, and sys.stderr.
        These arguments are optional and default to /dev/null.
        Note that stderr is opened unbuffered, so
        if it shares a file with stdout then interleaved output
        may not appear in the order that you expect.
    '''
    import os
    import sys
    
    # Do first fork.
    try: 
        pid = os.fork() 
        if pid > 0: sys.exit(0) # Exit first parent.
    except OSError, e: 
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
        
    # Decouple from parent environment.
    os.chdir("/") 
    os.umask(0) 
    os.setsid() 
    
    # Do second fork.
    try: 
        pid = os.fork() 
        if pid > 0: sys.exit(0) # Exit second parent.
    except OSError, e: 
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    
    # Open file descriptors and print start message
    if not stderr:
        stderr = stdout
        
    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)
    pid = str(os.getpid())
    if pidfile:
        f = file(pidfile,'w+')
        f.write("%s\n" % pid)
        f.close()
    
    # Redirect standard file descriptors.
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def play(f):
    
    header = f.read(WAV_HEADER_SIZE)
    format, nchannels, framerate, datarate, datalength \
            = wav_header_unpack(header)

    # Open the device in playback mode. 
    out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK)

    # Set attributes: Mono, 8000 Hz, 16 bit little endian frames
    out.setchannels(2)
    out.setrate(framerate)
    out.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    
    # The period size controls the internal number of frames per period.
    # The significance of this parameter is documented in the ALSA api.

    # rs = framerate / 25
    # out.setperiodsize(rs)

    data = f.read()
    while data:
        # Read data from stdin
        out.write(data)
        data = f.read()

if __name__ == '__main__':

    if len(sys.argv) > 1:
        bf = open(sys.argv[1], 'rb')
    else:
        bf = open(BEEP, 'rb')
        
    beep = cStringIO.StringIO(bf.read())
    bf.close()

    try:
        beepdev = open("/dev/beep")
    except IOError:
        print "Can't open beep device."
        sys.exit(0)

    try:
        daemonize(pidfile = '/var/run/alsabeepd.pid')
        
        while True:
            if beepdev.read(1):
                play(beep)
                beep.seek(0)
            else:
                continue
    finally:
        beepdev.close()

    
