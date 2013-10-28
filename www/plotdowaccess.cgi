#!/usr/bin/perl -w
#
# Plot number of DOW access per turn
# Returns a PNG image.
#

use strict;

use GD::Graph::lines;

use dow;

my($Donor);

$Donor = ProcessDowCommandline($Donor);

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: plotdowaccess.cgi\n");
}

sub GeneratePage {
    my($minturn, $maxturn, @x, @y, $sth, $row, $graph, @data, $ymin, $ymax, $i);
    $minturn = SelectOne("select min(turn) from dowaccess;");
    $maxturn = SelectOne("select max(turn) from dowaccess;");
    $sth = mydo("select turn, count(*) from dowaccess group by turn;");
    for ($i = $minturn; $i <= $maxturn; $i++) {
	push(@x, $i);
	push(@y, undef);
    }
    # @x = ($minturn .. $maxturn);
    # @y = map { undef } @x;
    $ymin = 100000;
    $ymax = -10000;
    while ($row = $sth->fetchrow_hashref()) {
	$y[$row->{turn} - $minturn] = $row->{count};
	if ($row->{count} < $ymin) {
	    $ymin = $row->{count};
	}
	if ($row->{count} > $ymax) {
	    $ymax = $row->{count};
	}
    }
    $sth->finish();
    ($ymin, $ymax) = GetRoundedRange($ymin, $ymax);
    add("Pragma: no-cache\nExpires: -1\nContent-type: image/png\n\n");
    @data = (\@x, \@y);
    $graph = GD::Graph::lines->new(1024, 960);
    $graph->set(xlabel => 'Turn',
		ylabel => 'Number of Accesses',
		title => "Number of DOW Accesses By Turn",
		y_min_value => 0,
		y_max_value => $ymax,
		x_label_skip => 10);
    add($graph->plot(\@data)->png);
}
