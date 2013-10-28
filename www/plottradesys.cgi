#!/usr/bin/perl -w
#
# Plot trade history of all resources at a system.
# Returns a PNG image.
#

use strict;

use GD::Graph::lines;

use dow;

my($Donor, $System);

$Donor = ProcessDowCommandline($Donor);

if ($#ARGV != 0) {
    usage();
}

$System = CanonicalizeSystem($ARGV[0]);

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: plottradesys.cgi?System%20Name\n");
}

sub GeneratePage {
    my($minturn, $maxturn, @x, @data, $i, %restoi, $res, $ncol, @legend);
    my($sth, $row, $graph, $ymin, $ymax);

    $minturn = SelectOne("select min(turn) from trade where system=?;", $System);
    $maxturn = SelectOne("select max(turn) from trade where system=?;", $System);

    $ncol = SelectOne("select count(resource) from trade where system=? and turn=?;", $System, $maxturn);

    # Set everything to undef

    @x = ($minturn .. $maxturn);
    push(@data, [@x]);
    for ($i = 0; $i < $ncol; $i++) {
	push(@data, [ map { undef } @x ]);
    }
    
    $i = 1;
    foreach $res (SelectAll("select distinct resource from trade where system=?;",
			    $System)) {
	push(@legend, $res);
	$restoi{$res} = $i++;
	if (nbuyers($res, $maxturn) == 2) {
	    push(@legend, $res);
	    $restoi{"$res-low"} = $i++;
	}
    }
    $ymin = 100000;
    $ymax = -10000;

    $sth = mydo("select turn, resource, min(price), max(price) from trade where system=? group by turn, resource;", $System);
    while ($row = $sth->fetchrow_hashref()) {
	if ($row->{max} > $ymax) {
	    $ymax = $row->{max};
	}
	if ($row->{min} < $ymin) {
	    $ymin = $row->{min};
	}
	$data[$restoi{$row->{resource}}]->[$row->{turn} - $minturn] = $row->{max};
	if (nbuyers($row->{resource}, $row->{turn}) == 2) {
	    $data[$restoi{"$row->{resource}-low"}]->[$row->{turn} - $minturn] = $row->{min};
	}
    }
    $sth->finish();

    ($ymin, $ymax) = GetRoundedRange($ymin, $ymax);
    if ($ymin < 0) {
	$ymin = 0;
    }

    add("Pragma: no-cache\nExpires: -1\nContent-type: image/png\n\n");
    $graph = GD::Graph::lines->new(800, 600);
    $graph->set(xlabel => 'Turn',
		ylabel => 'Price',
		title => "Price of Resources at $System",
		y_min_value => $ymin,
		y_max_value => $ymax
		);
    $graph->set_legend(@legend);
    add($graph->plot(\@data)->png);
}


sub nbuyers {
    my($res, $turn) = @_;
    my($sth, $row, $buyers);
    # How many buyers?
    $sth = mydo("select * from trade where system=? and resource=? and turn=?;",
		$System, $res, $turn);
    $row = $sth->fetchrow_hashref();
    if (!defined($row)) {
	herror("Failed to find trade data for system $System resource $res turn $turn");
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
