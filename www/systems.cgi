#!/usr/bin/perl -w
#
# Show all systems.
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
    herror("Usage: systems.cgi?-m");
}

sub GeneratePage {
    my(@hab, @nonhab, $sth, $row, $sysstr);

    $sth = mydo("select system from starcoords order by system;");
    while ($row = $sth->fetchrow_hashref()) {
	if ($opt_m) {
	    $sysstr = $row->{system};
	} else {
	    $sysstr = "<a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a>\n";
	}

	if ($row->{system} =~ /^Star \#[0-9]+$/){
	    push(@nonhab, $sysstr);
	} else {
	    push(@hab, $sysstr);
	}
    }
    add(DOW_HTML_Header($Donor, "DOW Information - All Systems"));
    add("<h1>DOW Information - All Systems</h1>");
    if ($opt_m) {
	add(MakeMap($Donor->{ship}, \@nonhab, \@hab));
	add("<hr><img src=\"bigred.gif\"> NonHabitable Systems<br>\n");
	add("<img src=\"biggreen.gif\"> Habitable Systems<br>\n");
    } else {
	add("<table>\n");
	add(MakeHTMLTable(6, @hab, @nonhab));
	add("</table>");
    }
    add(DOW_HTML_Footer($Donor));
}

