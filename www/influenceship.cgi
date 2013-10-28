#!/usr/bin/perl -w
#
# Show influence for a ship.
#

use strict;

use dow;

my($Donor, $Ship);

$Donor = ProcessDowCommandline();

if (! $Donor->{influence}) {
    herror("You must provide influence information to view influence information");
}

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
    herror("Usage: influenceship.cgi?Ship");
}

sub GeneratePage {
    my($sth, $row, $totalvotes, $turn, $str);

    $turn = SelectOne("select max(turn) from turnupdate;");

    $str = "select distinct on (location) * from influence where donated=true order by location, turn desc";

    $totalvotes = SelectOne("select sum(votes) from ($str) as orig where ship=?;", $Ship);
    
    $sth = mydo("select * from ($str) as orig where ship=? order by votes, system, race;", $Ship);    
    add(DOW_HTML_Header($Donor, "DOW - Influence of $Ship"));
    add("<h1>DOW - Influence of <a href=\"shipsummary.cgi?$Ship\">$Ship</a></h1>");
    if (!defined($totalvotes) || $totalvotes =~ /^\s*$/) {
	$totalvotes = 0;
    }
    add("<p>Total votes for $Ship: $totalvotes\n<p>\n");

    add("<table border>\n");
    add("<tr><th>System</th><th>Race</th><th>Enemy?</th><th>Politics</th><th>Location</th><th>Votes</th><th>Influence</th><th>Updated</th>\n");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr>\n");
	add(" <td><a href=\"influencesys.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a></td>");
	add(" <td><a href=\"alien.cgi?$row->{race}\">$row->{race}</a></td>\n");
	if (ExistsSelect("select * from enemies where turn=? and donorid=? and who=?;", $turn, $Donor->{donorid}, $row->{race})) {
	    add(" <td>Yes</td>\n");
	} else {
	    add(" <td>No</td>\n");
	}
	add(" <td>" . SelectOne("select area from aliens where race=?;", $row->{race}) . "</td>\n");
	if ($row->{votes} == 1) {
	    add(" <td>Colony $row->{location}</td>\n");
	} elsif ($row->{votes} == 6 || $row->{votes} == 8) {
	    add(" <td>Homeworld $row->{location}</td>\n");
	} else {
	    herror("Expected 1, 6, or 8 votes. Shouldn't happen!");
	}
	add(" <td>$row->{votes}</td>\n");
	add(" <td>$row->{influence}</td>\n");
	add(" <td>$row->{turn}</td>\n");
	add("</tr>\n");
    }
    add("</table>\n");
    add(DOW_HTML_Footer($Donor));
}
