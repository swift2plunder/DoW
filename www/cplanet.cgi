#!/usr/bin/perl -w

use strict;
use Getopt::Std;

use GD;

use vars qw($opt_a $opt_s $opt_n);

$opt_n = 19;
$opt_a = 'e';
$opt_s = '';
getopts('a:s:n:') or usage();

if ($#ARGV != -1) {
    usage();
}

cplanet();

sub usage {
    print STDERR "Usage: cplanet.cgi?-a+esmw+-s+esnw+-n+19\n";
    exit;
}

sub cplanet {
    my($im);
    my(@pies, @sensor, $angle, $start, $r, $i, $black);

    $im = new GD::Image($opt_n, $opt_n);
    $im->transparent($im->colorAllocate(255,255,255));
    $black = $im->colorAllocate(0,0,0);

    # Engineering orange
    if ($opt_a =~ /e/) {
	push(@pies, $im->colorAllocate(255,200,50));
	if ($opt_s =~ /e/) {
	    push(@sensor, 1);
	} else {
	    push(@sensor, 0);
	}
    }
    # Science blue
    if ($opt_a =~ /s/) {
	push(@pies, $im->colorAllocate(0, 0, 255));
	if ($opt_s =~ /s/) {
	    push(@sensor, 1);
	} else {
	    push(@sensor, 0);
	}
    }
    # Medical green
    if ($opt_a =~ /m/) {
	push(@pies, $im->colorAllocate(0, 255, 0));
	if ($opt_s =~ /m/) {
	    push(@sensor, 1);
	} else {
	    push(@sensor, 0);
	}
    }
    # Weaponry green
    if ($opt_a =~ /w/) {
	push(@pies, $im->colorAllocate(255, 0, 0));
	if ($opt_s =~ /w/) {
	    push(@sensor, 1);
	} else {
	    push(@sensor, 0);
	}
    }
    if ($#pies < 0) {
	usage();
    }

    $angle = 360/($#pies+1);
    $r = $opt_n/2;
    $i = 0;
    for ($start = 180; $start < 180+360; $start += $angle) {
	$im->filledArc($r, $r, 2*$r-3, 2*$r-3,
		       $start, $start+$angle-1, $pies[$i], gdArc);
	if ($sensor[$i]) {
	    $im->arc($r, $r, 2*$r, 2*$r, $start, $start+$angle-1, $black);
	}
	$i++;
    }
#    $im->rectangle(1,1,$opt_n-1,$opt_n-1,$black);

    print "Content-type: image/png\n\n";
    binmode STDOUT;
    print $im->png();	
}
