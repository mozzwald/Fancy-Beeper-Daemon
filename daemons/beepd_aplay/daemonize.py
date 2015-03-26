#!/usr/bin/python
#
'''\
Python code to turn a unix program into a daemon
mocons.lib.utils.daemonize.py
jjk  06/25/97  001
jjk  04/15/98  002  renamed from MdcBecomeDaemon.py

**works only on unix - NT does not support fork() command

from comp.lang.python postings
	Conrad Minshall <conrad@apple.com> 8/3/96
	Fredrik Lundh <Fredrik_Lundh@ivab.se> 8/5/96
	Monty Zukowski <monty@tbyte.com>	8/6/96

usage
	from mocons.lib.utils import daemonize
	daemonize.become_daemon(daemon_home_directory_name)

To start a test Daemon:
	daemonize.py test

'''


def become_daemon(ourHomeDir='.'):
	"""Robustly turn us into a UNIX daemon, running in ourHomeDir.
	XXX on SVR4 some claim you should re-fork after the setsid()
	jjk  06/25/97  001
	"""
	import os
	import sys
	if os.fork() != 0:  # launch child and...
		os._exit(0)     # kill off parent
	os.setsid()
	os.chdir(ourHomeDir)
	os.umask(0)
	sys.stdin.close()
	#sys.stdout.close()
	#sys.stderr.close()
	sys.stdout = NullDevice()
	sys.stderr = NullDevice()
	for z in range(3, 256):
		try: os.close(z)
		except: pass

class NullDevice:
	"""A substitute for stdout and stderr that writes to nowhere
	jjk  06/25/97  001
	"""

	def write(self, s):
		"""accept a write command, but do nothing
		jjk  06/25/97  001
		"""
		pass

def test():
	"""test become_daemon(). Launch a daemon that writes the time
	to a file every minute
	jjk  06/25/97  001
	"""
	import os
	import time
	filename = 'daemonize.test.out'
	sleepSeconds = 60

	print
	print 'Starting a test Daemon:'
	print '    every', sleepSeconds, "seconds, the daemon's process id"
	print '    and the the current time will be appended'
	print '    to the file', filename
	print 'You can view the output as it changes with:'
	print '    tail -f', filename
	print 'To stop the daemon, determine its PID from'
	print 'the output file, and use the kill command:'
	print '    kill <processid>'
	
	become_daemon('.')
	pid = os.getpid()	
	f = open(filename, 'a')
	f.write('\n\n*****Starting Test Daemon, PID: %d\n'%pid)
	f.close()
	while(1):
		ctime = time.asctime(time.localtime(time.time()))
		f = open(filename, 'a')
		f.write('PID: %d  Time: %s\n'%(pid, ctime))
		f.close()
		time.sleep(sleepSeconds)

if (__name__ == '__main__'):
	import sys, string
	if (len(sys.argv)>1):
		if (string.lower(sys.argv[1])=='test'):
			test()
	else:
		print
		print 'daemonize.py'
		print 'Python code to turn a unix program into a daemon'
		print 'To start a test Daemon:'
		print '     daemonize.py test'

