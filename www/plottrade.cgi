#!/usr/bin/perl -w
#
# Plot trade history of a single good at a single system.
# Returns a PNG image.
#

use strict;
use POSIX;
use GD::Graph::lines;

use dow;

my($Donor, $System, $Resource, $Width);

$Donor = ProcessDowCommandline($Donor);

if ($#ARGV == 2) {
    $Width = $ARGV[2];
} else {
    $Width = 800;
}

if ($#ARGV == 1 || $#ARGV == 2) {
    $System = CanonicalizeSystem($ARGV[0]);
    $Resource = $ARGV[1];
    $Resource =~ s/\\//g;
} else {
    usage();
}

if ($Width > 10000) {
    $Width = 10000;
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: plottrade.cgi?System%20Name+Resource%20Name[+width]\n");
}

sub GeneratePage {
    my($minturn, $maxturn, @x, @y1, @y2, $sth, $row, $buyers, $i);
    my(@data, $graph);
    $minturn = SelectOne("select min(turn) from trade where system=? and resource=?;", $System, $Resource);
    $maxturn = SelectOne("select max(turn) from trade where system=? and resource=?;", $System, $Resource);

    # How many buyers?
    $sth = mydo("select * from trade where system=? and resource=? and turn=?;",
		$System, $Resource, $maxturn);
    $row = $sth->fetchrow_hashref();
    if (!defined($row)) {
	herror("Failed to find trade data for system $System resource $Resource turn");
    }
    $row = $sth->fetchrow_hashref();
    if (defined($row)) {
	$buyers = 2;
    } else {
	$buyers = 1;
    }
    $sth->finish();

    # Set everything to undef

    @x = ($minturn .. $maxturn);
    @y1 = map { undef } @x;
    @y2 = map { undef } @x;

    $sth = mydo("select turn, min(price), max(price) from trade where system=? and resource=? group by turn;", $System, $Resource);
    while ($row = $sth->fetchrow_hashref()) {
	$y1[$row->{turn} - $minturn] = $row->{max};
	if ($buyers == 2) {
	    $y2[$row->{turn} - $minturn] = $row->{min};
	}
    }
    $sth->finish();

    add("Pragma: no-cache\nExpires: -1\nContent-type: image/png\n\n");

    if ($buyers == 1) {
	@data = (\@x, \@y1);
    } else {
	@data = (\@x, \@y1, \@y2);
    }
    
    $graph = GD::Graph::lines->new($Width, 600);
    $graph->set(xlabel => 'Turn',
		ylabel => 'Price',
		title => "Price of $Resource at $System");
    add($graph->plot(\@data)->png);
}

