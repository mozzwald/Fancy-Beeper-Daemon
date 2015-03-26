/*
 *  Console beep daemon for Zipit Z2
 *
 *  Runs the command provided by the user when there
 *  is a console bell notification
 *
 *  http://mozzwald.com
 */

/*
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License version 2 as published by
 * the Free Software Foundation
 */


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>

#define BEEP_DEV "/dev/beep"
#define POLL_TIMEOUT (3 * 1000) /* 3 seconds */
#define MAX_BUF 64

/****************************************************************
 * beep_fd_open
 ****************************************************************/

int beep_fd_open()
{
	int fd, len;
	char buf[MAX_BUF];

	len = snprintf(buf, sizeof(buf), BEEP_DEV);
 
	fd = open(buf, O_RDONLY | O_NONBLOCK );
	if (fd < 0) {
		perror("beep_fd_open");
		exit(1);
	}
	return fd;
}

/****************************************************************
 * beep_fd_close
 ****************************************************************/

int beep_fd_close(int fd)
{
	return close(fd);
}

/****************************************************************
 * Main
 ****************************************************************/
int main(int argc, char **argv, char **envp)
{
	struct pollfd fdset[1];
	int nfds = 2;
	int beep_fd, timeout, rc;
	char *buf[MAX_BUF];
	int len;

	if (argc < 2) {
		printf("Usage: beepcmd \"<command>\"\n\n");
		printf("Runs a command when there is a console beep by reading /dev/beep\n");
		exit(-1);
	}

	/* open the device file */
	beep_fd = beep_fd_open();

	timeout = POLL_TIMEOUT;
 
	while (1) {
		memset((void*)fdset, 0, sizeof(fdset));

		fdset[0].fd = beep_fd;
		fdset[0].events = POLLIN;

                lseek(fdset[0].fd, 0, SEEK_SET); /* return to beginning of stream/file */

		rc = poll(fdset, nfds, timeout);      

		if (rc < 0) {
			printf("\npoll() failed!\n");
			return -1;
		}
      
		if (fdset[0].revents & POLLIN) {
			len = read(fdset[0].fd, buf, MAX_BUF);
			//printf("BEEP interrupt occurred\n");
			system(argv[1]);
		}
		fflush(stdout);
	}

	beep_fd_close(beep_fd);
	return 0;
}
