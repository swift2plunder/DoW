#!/usr/bin/perl -w
#
# Show plagues
#

use strict;
use Getopt::Std;

use dow;

use vars qw($opt_m);

my $Donor = ProcessDowCommandline();

getopts('m') or usage();

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: plagues.cgi?-m<br> &nbsp; -m Use map view (otherwise, listview)");
}

sub GeneratePage {
    my($sth, $row, $turn, @cured, @uncured, $sysstr);

    $turn = SelectOne("select max(turn) from plagues where donorid=?;",
		      $Donor->{donorid});
    add(DOW_HTML_Header($Donor, "DOW Plague Information for $Donor->{ship}"));
    add("<h1>DOW Plague Information for $Donor->{ship}</h1>\n");
    if ($opt_m) {
	add("<p>Go to <a href=\"plagues.cgi\">List View</a><hr>");
    } else {
	add("<p>Go to <a href=\"plagues.cgi?-m\">Map View</a><p>");
    }

    $sth = mydo("select * from sysplagues order by system;");

    while ($row = $sth->fetchrow_hashref()) {
	if ($opt_m) {
	    $sysstr = $row->{system};
	} else {
	    $sysstr = "<a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a>\n";
	}
	if (ExistsSelect("select turn from plagues where donorid=? and system=? and turn=?;", $Donor->{donorid}, $row->{system}, $turn)) {
	    push(@cured, $sysstr);
	} else {
	    push(@uncured, $sysstr);
	}
    }
    if ($opt_m) {
	add(MakeMapImage($Donor->{ship}, \@uncured, 'plague.jpg', \@cured, 'biggreen.gif'));
	add("<hr><img src=\"plague.jpg\"> Uncured Plague<br>\n");
	add("<img src=\"biggreen.gif\"> Cured Plague<br>\n");
    } else {
	add("<p><table border>\n");
	add(MakeHTMLTable(2, "<em>Uncured Plagues</em>", @uncured, " &nbsp; ", "<em>Cured Plagues</em>", @cured));
	add("</table>");
    }
    add(DOW_HTML_Footer($Donor));
}

	
