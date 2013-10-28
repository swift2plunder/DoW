#!/usr/bin/perl -w
#
# Show info about one alien
#

use strict;
use dow;

my($Donor, $Race);

$Donor = ProcessDowCommandline();

if ($#ARGV != 0) {
    usage();
}

$Race = $ARGV[0];

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: alien.cgi?AlienRace");
}

sub GeneratePage {
    my($turn, $aliens, $mintech, $maxtech, $sth, $row, $seenturn, $system);

    $turn = SelectOne("select max(turn) from turnupdate;");
    add(DOW_HTML_Header($Donor, "DOW Alien Race Information for $Race"));
    add("<h1>Alien Race Information for the $Race people</h1>\n");
    $aliens = SelectOneRowAsHash("select * from aliens where race=?;", $Race);
    add("<table>\n");
    if ($aliens->{skilllevel} > 1) {
	$mintech = TechLevelToName($aliens->{skilllevel}-1);
    } else {
	$mintech = "Primitive";
    }
    $maxtech = TechLevelToName($aliens->{skilllevel}+1);
    add("<tr><td>Tech Level</td><td>$mintech - $maxtech</td></tr>\n");
    add("<tr><td>Alignment</td><td>$aliens->{alignment}</td></tr>\n");
    add("<tr><td>Area</td><td>$aliens->{area}</td></tr>\n");

    add("<tr><td>Your Enemy?&nbsp;&nbsp;</td><td>");
    if (ExistsSelect("select * from enemies where donorid=? and who=? and turn=?;",
		     $Donor->{donorid}, $Race, $turn)) {
	add("Yes");
    } else {
	add("No");
    }
    add("</td></tr>\n");

    add("<tr><td>Homeworld</td><td><a href=\"system.cgi?" . UncanonicalizeSystem($aliens->{system}) . "\">$aliens->{system}</a></td></tr>\n");

    add("</table>\n");
    add("<p><table>\n");
    add("<tr><th align=left>Ship</th><th align=left>Last Seen&nbsp;</th><th align=left>System</th></tr>\n");

    $sth = mydo("select * from allships where turn=? and type=? and ship like ?;",
		$turn, "Alien", "$Race%");
    while ($row = $sth->fetchrow_hashref()) {
	$seenturn = SelectOne("select max(turn) from shiploc where ship=?;", 
			      $row->{ship});
	$system = SelectOne("select system from shiploc where ship=? and turn=?;",
			    $row->{ship}, $seenturn);
	add("<tr><td><a href=\"shipsummary.cgi?$row->{ship}\">$row->{ship}</a>&nbsp;&nbsp;</td>\n");
	add("<td>$seenturn</td><td><a href=\"system.cgi?$system\">$system</a></td></tr>\n");
    }
    $sth->finish();
    add("</table>\n");	    
    add("<p>Colonies:\n");
    add("<table>\n");
    $sth = mydo("select * from colonies where race=?;", $Race);
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr><td><a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a>&nbsp;&nbsp;</td>\n");
	add("<td><a href=\"res.cgi?$row->{resource}\">$row->{resource}</a></td>\n");
	add("</tr>\n");
    }
    add("</table>");
    $sth->finish();
    add(DOW_HTML_Footer($Donor));
}
