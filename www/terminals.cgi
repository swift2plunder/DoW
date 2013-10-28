#!/usr/bin/perl -w
#
# Show terminals.
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
    herror("Usage: terminals.cgi?-m<br> &nbsp; -m  Use map view (otherwise, listview)");
}

sub GeneratePage {
    my($sth, $row, $turn, @hacked, @unhacked, $sysstr, $fstr);
    my(@frags);

    $turn = SelectOne("select max(turn) from terminals where donorid=?;",
		      $Donor->{donorid});
    $sth = mydo("select * from fragments where turn=?;", $turn);
    while ($row = $sth->fetchrow_hashref()) {
	$fstr = $row->{fragment};
#	if (exists($row->{source}) && defined($row->{source})) {
#	    $fstr .= " ($row->{source})";
#	}
	push(@frags, $fstr);
    }
    $sth->finish();
    add(DOW_HTML_Header($Donor, "DOW Starnet Terminal Information for $Donor->{ship}"));
    add("<h1>DOW Starnet Terminal Information for $Donor->{ship}</h1>\n");
    add("See also <a href=\"http://janin.org/ninja/purges.html\">purges list</a> for a list of terminals that have recently been purged and may need repurging.");
    add("<p>Starnet fragments: ");
    if ($#frags >= 0) {
	add(join(", ", @frags));
    } else {
	add("None known");
    }
    if ($opt_m) {
	add("<p>Go to <a href=\"terminals.cgi\">List View</a><hr>");
    } else {
	add("<p>Go to <a href=\"terminals.cgi?-m\">Map View</a><p>");
    }
    
    $sth = mydo("select system from sysstarnet order by system;");

    while ($row = $sth->fetchrow_hashref()) {
	if ($opt_m) {
	    $sysstr = $row->{system};
	} else {
	    $sysstr = "<a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a>\n";
	}
	if (ExistsSelect("select turn from terminals where donorid=? and system=? and turn=?;", $Donor->{donorid}, $row->{system}, $turn)) {
	    push(@hacked, $sysstr);
	} else {
	    push(@unhacked, $sysstr);
	}
    }
    if ($opt_m) {
	add(MakeMap($Donor->{ship}, \@unhacked, \@hacked));
	add("<hr><img src=\"bigred.gif\"> Unaccessed Terminals<br>\n");
	add("<img src=\"biggreen.gif\"> Accessed Terminals<br>\n");
    } else {
	add("<table border>\n");
	add(MakeHTMLTable(2, "<em>Unaccessed Terminals</em>", @unhacked, " &nbsp; ", "<em>Accessed Terminals</em>", @hacked));
	add("</table>");
    }
    add(DOW_HTML_Footer($Donor));
}
