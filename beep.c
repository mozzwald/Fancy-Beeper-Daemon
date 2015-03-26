/*
 *  Fancy beeper driver for Linux
 *
 *  Copyright (c) 2004 Jason F. McBrayer
 *
 *  Based on pcspkr.c (c) 2002 Vojtech Pavlik and (c) 1992 Orest Zborowski
 *  Inspired by modreq_beep and oplbeep.
 *
 */

/*
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License version 2 as published by
 * the Free Software Foundation
 */

/* Kernel includes */
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/init.h>
#include <linux/input.h>
#include <linux/sched.h>
#include <asm/io.h>
#include <linux/miscdevice.h>
#include <asm/uaccess.h>
#if defined(CONFIG_MIPS) || defined(CONFIG_X86)
#include <asm/i8253.h>
#else
#include <asm/8253pit.h>
static DEFINE_SPINLOCK(i8253_lock);
#endif

/* Definitions */
#define BEEP_MAJOR 10
#define BEEP_MINOR 128
#undef DEBUG

/* Static data */
static DECLARE_WAIT_QUEUE_HEAD (beep_wait);
static char what_beep=0;
static int beep_listening=0;


MODULE_AUTHOR("Jason F. McBrayer <jmcbray@carcosa.net>");
MODULE_DESCRIPTION("Fancy beeper driver");
MODULE_LICENSE("GPL");

static char beep_name[] = "Fancy Beeper";
static struct input_dev *beep_dev;


static int close_beep(struct inode * inode, struct file * file)
{
  if (beep_listening >0)
    beep_listening--;
  return(0);
}

/*
 * open access to the beep, currently only one reading open is
 * allowed. We can do as many writes as we like. This really calls 
 * for some kind of buffering of events, something more accurate than
 * the simple static what_beep. Later.... 
 */

static int open_beep(struct inode * inode, struct file * file)
{
#ifdef DEBUG
  printk(KERN_WARNING "open_beep called.\n");
#endif
  switch(file->f_flags & O_ACCMODE)
    {
    case O_RDONLY:
      if (beep_listening)
        return -EBUSY;
      beep_listening++;
      what_beep=0; /* Zero means we don't have
                      any beeps waiting to be fetched */
      return 0;
    case O_NONBLOCK:
      return -EAGAIN;
    case O_WRONLY:
      return 0;
    default:
      return -EINVAL;
    }
}

static ssize_t read_beep(struct file * file, char * buffer, size_t len,
			 loff_t *ppos)
{
  size_t bytes_sent=0;

  /* Can't seek (pread) on this device */
  /* if (ppos != &file->f_pos) */
  /*     return -ESPIPE; */
  /* You can seek, but it doesn't do anything... */

  if (!access_ok(VERIFY_WRITE, buffer, sizeof(what_beep))) {
    what_beep = 0;
    return -EFAULT;
  }
  if (!beep_listening) /* Pretty improbable...*/
    {
      return -EAGAIN;
      /* Uh? Is this a good return value? */
    }
	
  /* OK, now for the fun bit.... I never did anything in kernel space
   * before, so if this is completely foolish, just tell me, OK?
   */
  if (wait_event_interruptible(beep_wait, what_beep))
    return -EINTR;
  
  while ((len>0) && (what_beep>0)) {
    put_user(what_beep, buffer);
    what_beep--;
    len--;
    bytes_sent++;
  }
#ifdef DEBUG
  printk("Beep!\n");
#endif
  return(bytes_sent);
}

struct file_operations beep_fops = {
  owner: THIS_MODULE,
  read: read_beep,
  open: open_beep,
  release: close_beep,
};

static struct miscdevice beep_miscdev = {
  BEEP_MINOR,
  "beep",
  &beep_fops
};


static int beep_event(struct input_dev *dev, unsigned int type,
                      unsigned int code, int value)
{
  unsigned int count = 0;
  unsigned long flags;

  if (type != EV_SND)
    return -1;

  switch (code) {
  case SND_BELL: if (value) value = 1000;
  case SND_TONE: break;
  default: return -1;
  } 
#ifdef DEBUG
  printk(KERN_WARNING "beep_event called with %d %d %d\n",
         type, code, value);
#endif

  if ( !beep_listening )
    {
      /* This code cribbed from pcspkr.c; if no beeper daemon is
         running, we fall back to a speaker beep. */
      
      if (value > 20 && value < 32767)
        count = PIT_TICK_RATE / value;
      
      spin_lock_irqsave(&i8253_lock, flags);
      
      if (count) {
        /* enable counter 2 */
        outb_p(inb_p(0x61) | 3, 0x61);
        /* set command for counter 2, 2 byte write */
        outb_p(0xB6, 0x43);
        /* select desired HZ */
        outb_p(count & 0xff, 0x42);
        outb((count >> 8) & 0xff, 0x42);
      } else {
        /* disable counter 2 */
		outb(inb_p(0x61) & 0xFC, 0x61);
      }
      
      spin_unlock_irqrestore(&i8253_lock, flags);
    }
  if (value) {
    what_beep=1;
    wake_up(&beep_wait);
  }
  return 0;
}

static int __init beep_init(void)
{
  beep_dev = input_allocate_device();
  
  beep_dev->evbit[0] = BIT(EV_SND);
  beep_dev->sndbit[0] = BIT(SND_BELL) | BIT(SND_TONE);
  beep_dev->event = beep_event;
  beep_dev->name = beep_name;

  input_register_device(beep_dev);

  printk(KERN_INFO "input: %s\n", beep_name);

  misc_register(&beep_miscdev);
        
  return 0;
}

static void __exit beep_exit(void)
{
  input_unregister_device(beep_dev);
  misc_deregister(&beep_miscdev);
}


module_init(beep_init);
module_exit(beep_exit);
