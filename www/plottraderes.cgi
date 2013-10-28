#!/usr/bin/perl -w
#
# Plot trade history of all systems selling given resource.
# Returns a PNG image.
#

use strict;

use GD::Graph::lines;

use dow;

my($Donor, $Resource);

$Donor = ProcessDowCommandline($Donor);

if ($#ARGV != 0) {
    usage();
}

$Resource = $ARGV[0];
$Resource =~ s/\\//g;

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: plottraderes.cgi?Resource%20Name\n");
}

sub GeneratePage {
    my($minturn, $maxturn, @x, @data, $i, %systoi, $sys, @legend);
    my($sth, $row, $graph, $ymin, $ymax);

    $minturn = SelectOne("select min(turn) from trade where resource=?;", 
			 $Resource);
    $maxturn = SelectOne("select max(turn) from trade where resource=?;", 
			 $Resource);

    # Set everything to undef

    @x = ($minturn .. $maxturn);
    push(@data, [@x]);
    for ($i = 0; $i < 8; $i++) {
	push(@data, [ map { undef } @x ]);
    }
    
    $i = 1;
    foreach $sys (SelectAll("select distinct system from trade where resource=?;",
			    $Resource)) {
	push(@legend, $sys);
	$systoi{$sys} = $i++;
	if (nbuyers($sys) == 2) {
	    push(@legend, $sys);
	    $systoi{"$sys-low"} = $i++;
	}
    }

    $ymin = 100000;
    $ymax = -10000;

    $sth = mydo("select turn, system, min(price), max(price) from trade where resource=? group by turn, system;", $Resource);
    while ($row = $sth->fetchrow_hashref()) {
	$data[$systoi{$row->{system}}]->[$row->{turn} - $minturn] = $row->{max};
	if ($row->{max} > $ymax) {
	    $ymax = $row->{max};
	}
	if ($row->{min} < $ymin) {
	    $ymin = $row->{min};
	}
	if (nbuyers($row->{system}) == 2) {
	    $data[$systoi{"$row->{system}-low"}]->[$row->{turn} - $minturn] = $row->{min};
	}
    }
    $sth->finish();
    ($ymin, $ymax) = GetRoundedRange($ymin, $ymax);

    add("Pragma: no-cache\nExpires: -1\nContent-type: image/png\n\n");
    $graph = GD::Graph::lines->new(800, 600);
    $graph->set(xlabel => 'Turn',
		ylabel => 'Price',
		title => "Prices of $Resource",
		y_min_value => $ymin,
		y_max_value => $ymax);
    $graph->set_legend(@legend);
    add($graph->plot(\@data)->png);
}


sub nbuyers {
    my($sys) = @_;
    my($sth, $row, $buyers, $turn);
    
    $turn = SelectOne("select max(turn) from trade where system=?;", $sys);
    $sth = mydo("select * from trade where system=? and resource=? and turn=?;",
		$sys, $Resource, $turn);
    $row = $sth->fetchrow_hashref();
    if (!defined($row)) {
	herror("Failed to find trade data for system $sys resource $Resource turn $turn");
    }
    $row = $sth->fetchrow_hashref();
    if (defined($row)) {
	$buyers = 2;
    } else {
	$buyers = 1;
    }
    $sth->finish();
    return $buyers;
}
