#!/usr/bin/perl -w
#
# Show latest ship configuration.
#

use strict;
use FileHandle;

use dow;

my($Donor, $Ship);

$Donor = ProcessDowCommandline();

if ($#ARGV != 0) {
    usage();
}

$Ship = $ARGV[0];
$Ship =~ s/\\//g;

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: shipconfig.cgi?Ship%20name");
}

sub GeneratePage {
    my($sth, $row, $line, $fh, $gotbody);
    if (! $Donor->{shipconfig}) {
	herror("You must donate ship configuration information to view ship configuration information");
    }
    $sth = mydo("select distinct on (ship) * from shipconfig where ship=? and donated=true order by ship, turn desc;", $Ship);

    $row = $sth->fetchrow_hashref();

    add(DOW_HTML_Header($Donor, "DOW - $Ship Ship Configuration"));

    if (!defined($row)) {
	add("<h1>DOW - $Ship Ship Configuration</h1>\n");
	add("<p>No donated ship configuration information for $Ship is available.\n");
	add(DOW_HTML_Footer($Donor));
	return;
    }

    $fh = new FileHandle($row->{path});
    if (!$fh) {
	herror("Couldn't get ship config from cache. This shouldn't happen!");
    }
    $gotbody = 0;
    while ($line = <$fh>) {
	if ($line eq "<BODY TEXT=\"Yellow\" BGCOLOR=\"Black\" LINK=\"White\" VLINK=\"Cyan\"><CENTER>\n") {
	    $gotbody = 1;
	    last;
	}
    }
    if (!$gotbody) {
	herror("Failed to find body line in ship config!");
    }
    add("<h1>DOW - $Ship Ship Configuration</h1>\n");
    add("<p>Configuration from turn $row->{turn}<p><hr><p>\n<center>");
    while ($line = <$fh>) {
	last if ($line eq "</CENTER></BODY></HTML>\n");
	add($line);
    }
    $fh->close();
    add("</center>\n<p>");
    add(DOW_HTML_Footer($Donor));
}
    

