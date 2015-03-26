ifneq ($(KERNELRELEASE),)
obj-m	:= beep.o

else
# ifeq ($(ARCH), x86_64)
# KDIR	:= /lib64/modules/$(shell uname -r)/build
# else
# KDIR	:= /lib/modules/$(shell uname -r)/build
# endif
KDIR	:= $(shell if [ -d /lib64 ] && [ `uname -m` = amd64 ]; then echo /lib64; else echo /lib; fi;)/modules/`uname -r`/build
PWD		:= `pwd`

default:
	$(MAKE) -C $(KDIR) SUBDIRS=$(PWD) modules

endif

clean:
	rm -f *.o *.ko core* beep.mod.c .beep*.cmd modules.order Module.markers \
		Module.symvers
	rm -rf .tmp_versions

