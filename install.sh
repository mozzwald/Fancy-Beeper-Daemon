#!/bin/sh

# Build and install module
if [ -d /lib64 ] && [ `uname -m` = amd64 ]
then
    LIBDIR=/lib64
else
    LIBDIR=/lib
fi

make
install -d $LIBDIR/modules/`uname -r`/drivers/input/misc/
install -m 644 beep.ko $LIBDIR/modules/`uname -r`/drivers/input/misc/beep.ko
/sbin/depmod -a
/sbin/modprobe beep

# Not needed for devfs or udev
if ! pgrep udev>/dev/null
then 
mknod /dev/beep c 10 128
chmod ugo+r /dev/beep
fi
