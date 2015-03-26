#!/usr/bin/perl

# beepd_esd.pl - by Frank Johnson <ratty@they.org>
# Usage: beepd_esd.pl [something.wav]
#    beepd_esd.pl reads from your /dev/misc/beep device and plays a sound
#    every time you would normally hear a console beep
#    The default sound is /usr/share/sounds/ding.wav which can
#    be conveniently pirated from an M$ OS near you.

if ($ARGV[0])
{ $file = $ARGV[0]; }
else
{ $file = "/usr/share/sounds/ding.wav"; }

die "$file is not a file\n" if (! -f $file);

open(BEEP,"/dev/beep") || die "Can't open /dev/beep\n";

fork && exit;
while (1)
{
	if (read(BEEP,$a,1))
	{
		fork &&	exec ("/usr/bin/esdplay", "$file");
	}
}

close BEEP;
