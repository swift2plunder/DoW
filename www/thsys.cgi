#!/usr/bin/perl -w
#
# Allows user to select a system and plot its trade history
#

use strict;

use dow;

my($Donor, $System);

$Donor = ProcessDowCommandline($Donor);

if ($#ARGV == -1) {
    GenerateSelection();
} elsif ($#ARGV == 0) {
    $System = CanonicalizeSystem($ARGV[0]);
    GeneratePlot();
} else {
    usage();
}

PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: thsys.cgi OR thsys.cgi?System%20Name<p>\nWith no args, gives possible selections. With args, shows plot.");
}

sub GeneratePlot {
    add(DOW_HTML_Header($Donor, "DOW - Trade History at $System"));
    add("<img src=\"plottradesys.cgi?" . UncanonicalizeSystem($System) . "\">\n");
    add(DOW_HTML_Footer($Donor));
}

sub GenerateSelection {
    my($sys, @sys);
	
    add(DOW_HTML_Header($Donor, "DOW - Trade History By System"));
    add("<h1>Trade History by System</h1>\n");
    add("<table>\n");
    add(MakeHTMLTable(6, map { "<a href=\"thsys.cgi?" . UncanonicalizeSystem($_) . "\">$_</a>&nbsp;&nbsp;" } SelectAll("select distinct system from trade order by system;")));
    add("</table>\n");
    add(DOW_HTML_Footer($Donor));
}

	
