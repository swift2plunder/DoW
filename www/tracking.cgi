#!/usr/bin/perl -w

use strict;
use Getopt::Std;

use dow;

my ($Donor);

use vars qw($opt_t);

$Donor = ProcessDowCommandline();

if (!$Donor->{shiploc}) {
    herror("You must donate ship location information to see ship locations");
}

$opt_t = SelectOne("select max(turn) from turnupdate;");
getopts('t:') or usage();

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();
CloseDB();

exit;

sub usage {
    herror("Usage: tracking.cgi[?-t+turn]");
}

sub GeneratePage {
    my($sth, $row, $system, $paired, $seenturn);
    $sth = mydo("select tracked from tracking where ship=?;", $Donor->{ship});
    add(DOW_HTML_Header($Donor, "Tracking page for $Donor->{ship}"));
    add("<h1>Tracking Page for $Donor->{ship}, Turn $opt_t</h1>\n");
    add("This page lists information on ships you are currently tracking. To change which ships you track, go to <a href=\"settracking.cgi\">this page</a>.<p>\n");
#    add("The <em>Traced</em> column indicates if any ship in DOW is tracing the given ship.<p>\n");
    add("<table>\n");
    add("<tr><th align=left>Ship&nbsp;&nbsp;</th><th align=left>Last Seen</th><th align=left>&nbsp;&nbsp;Paired With</th></tr>\n");
    while ($row = $sth->fetchrow_hashref()) {
	next if (!ExistsSelect("select * from activeships where ship=? and turn=?;", $row->{tracked}, $opt_t));
	add("<tr>\n");
	add(" <td><a href=\"shipsummary.cgi?$row->{tracked}\">$row->{tracked}</a>&nbsp;&nbsp;</td>\n");
	$seenturn = SelectOne("select max(turn) from shiploc where ship=? and turn<=? and donated=true;", 
			      $row->{tracked}, $opt_t);
	$system = SelectOne("select system from shiploc where ship=? and turn=? and donated=true;",
			    $row->{tracked}, $seenturn);
	add(" <td><a href=\"system.cgi?" . UncanonicalizeSystem($system) . "\">$system</a>");
	if ($seenturn != $opt_t) {
	    add(" ($seenturn)");
	}
	add("</td>\n");
	$paired = PairedShip($row->{tracked}, $opt_t, 1);
	if (defined($paired)) {
	    add(" <td>&nbsp;&nbsp;<a href=\"shipsummary.cgi?$paired\">$paired</a></td>\n");
	} else {
	    add(" <td>&nbsp;</td>\n");
	}
#	if (ExistsSelect("select * from traces where turn=? and ship=?;",
#			 $opt_t, $row->{tracked})) {
#	    add("<td>&nbsp;&nbsp;<font size=\"-1\">(Traced)</font></td>\n");
#	} else {
#	    add("<td>&nbsp;</td>\n");
#	}
	add("</tr>\n");
    }
    add("</table>");
    $sth->finish();
    add(DOW_HTML_Footer($Donor));
}
