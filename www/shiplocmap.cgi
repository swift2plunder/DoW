#!/usr/bin/perl -w
######################################################################
#
# For privacy reasons, restricted access.
#

use strict;

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
    herror("Usage: shiplocmap.cgi?Ship%20name");
}

sub GeneratePage {
    my($sth, $row, %density, %turn, $mind, $maxd, $mint, $maxt);
    my($system, $density, $turn, %html, $atsystem);
    if ($Ship ne $Donor->{ship}) {
	herror("For now, you can only see this info about your own ship. I'll post about this shortly.");
    }
    $atsystem = SelectOne("select system from shiploc where ship=? order by turn desc limit 1;", $Ship);
    add(DOW_HTML_Header($Donor, "DOW $Ship Location Information"));
    add("<h1>DOW <a href=\"shipsummary.cgi?$Ship\">$Ship</a> Location Information</h1>\n");
    add("<p>Go to <a href=\"shiploc.cgi?$Ship\">List View</a>\n");
    add("<p>Size indicates how <em>frequently</em> $Ship has visited the system. Darkness indicates how <em>recently</em> $Ship has visited the system. The system with red text is where $Donor->{ship} was last seen. The system with the red circle is where $Ship was last seen.\n");
    add("<p><hr><p>\n");
    $mint = 10000;
    $maxt = -1;
    $mind = 10000;
    $maxd = -1;
    $sth = mydo("select system, max(turn), count(*) from shiploc where ship=? group by system;", $Ship);
    while ($row = $sth->fetchrow_hashref()) {
	$density{$row->{system}} = $row->{count};
	$turn{$row->{system}} = $row->{max};
	if ($row->{count} < $mind) {
	    $mind = $row->{count};
	}
	if ($row->{count} > $maxd) {
	    $maxd = $row->{count};
	}
	if ($row->{max} < $mint) {
	    $mint = $row->{max};
	}
	if ($row->{max} > $maxt) {
	    $maxt = $row->{max};
	}
    }
    $sth->finish();
    #print STDERR "mint=$mint maxt=$maxt\nmind=$mind maxd=$maxd\n";
    foreach $system (keys %turn) {
	$density = 10+int(10*($density{$system}-$mind)/($maxd - $mind));
	$turn = 13-int(13*($turn{$system}-$mint)/($maxt - $mint));
	if ($system eq $atsystem) {
	    $html{$system} = sprintf("<img border=none src=\"planet.cgi?%d+%d+%%23%01xf%01xf%01xf\">", $density, $density, 15, $turn, $turn);
	} else {
	    $html{$system} = sprintf("<img border=none src=\"planet.cgi?%d+%d+%%23%01xf%01xf%01xf\">", $density, $density, $turn, $turn, $turn);
	}
#	print STDERR "$system $density $turn $html{$system}\n";
    }
    add(MakeMapGeneralNew($Donor->{ship}, \%html, "&nbsp;"));
    add(DOW_HTML_Footer($Donor));
}
