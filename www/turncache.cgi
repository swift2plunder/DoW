#!/usr/bin/perl -w
#
# Show turn cache.
#
# With no arguments, list them all. With one argument, show that turn.
#

use strict;

use File::Find;
use FileHandle;

use dow;

my($TurnDir, $Donor, @Turns);

$TurnDir = '/Path/to/turns';

$Donor = ProcessDowCommandline();

if ($#ARGV == -1) {
    GenerateList();
} elsif ($#ARGV == 0) {
    GenerateTurn($ARGV[0]);
} else {
    usage();
}

PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: turncache.cgi or turncache.cgi?1023");
}

sub GenerateList {
    my($turn);
    find(\&wanted, $TurnDir);
    add(DOW_HTML_Header($Donor, "DOW - Cached Turns for $Donor->{ship}"));
    add("<h1>DOW - Cached Turns for $Donor->{ship}</h1>\n");
    add("<p>\n");
    foreach $turn (sort { $b <=> $a } @Turns) {
	add("<a href=\"turncache.cgi?$turn\">$turn</a><br>\n");
    }

    add("\n\n");
    add(DOW_HTML_Footer($Donor));
}

sub GenerateTurn {
    my($turn) = @_;
    my($fh, $line);
    $fh = new FileHandle("$TurnDir/$turn/$Donor->{donorid}.html") or
	herror("Failed to find cached entry, turn $turn for $Donor->{ship}");
    add("Content-type: text/html\n\n");
    while ($line = <$fh>) {
	add($line);
    }
    $fh->close();
}

sub wanted {
    if ($File::Find::name =~ m|$TurnDir/([0-9]+)/$Donor->{donorid}\.html|) {
	push(@Turns, $1);
    }
}
