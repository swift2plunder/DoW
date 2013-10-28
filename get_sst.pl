#!/usr/bin/perl -w
#
# Get and store the SST file for the current turn.
#

use strict;
use FileHandle;
use LWP::Simple;

my($Turn, $TurnFile, $URL);

if ($ARGV[0] eq '-t') {
    shift;
}

$Turn = shift or error("Usage: get_sst.pl turn");

$TurnFile = "/Path/to/tbg/sst/$Turn.html";
$URL = "http://tbg.fyndo.com/tbg/times.html";

if (-e $TurnFile) {
    error("SST for turn $Turn already exists. Skipping.");
}

download_sst();
check_sst();

exit();

sub download_sst {
    my($i);
    for ($i = 1; $i <= 3; $i++) {
	if (is_success(getstore($URL, $TurnFile))) {
	    last;
	}
	warning("getstore of SST times.html failed, try $i");
    }
    if ($i == 4) {
	error("getstored failed 3 times. Giving up.");
    }
}

sub check_sst {
    my($fh, $line, $turn, $gotit);
    $gotit = 0;
    $fh = new FileHandle($TurnFile) or error("Couldn't open SST $TurnFile.");
    while ($line = <$fh>) {
	if ($line =~ m|^<H1>Issue ([0-9]+) - Stardate|) {
	    $turn = $1;
	    if ($Turn != $turn) {
		unlink($TurnFile) or error("Couldn't unlink SST $TurnFile.");
		error("Turn mismatch in SST. Expected $Turn, got $turn.");
	    }
	    $gotit = 1;
	    last;
	}
    }
    if (!$gotit) {
	error("Failed to extract turn from sst $TurnFile.");
    }
    $fh->close();
}

sub error {
    print STDERR "Error: ", join("", @_), "\n";
    exit;
}

sub warning {
    print STDERR "Warning: ", join("", @_), "\n";
}
