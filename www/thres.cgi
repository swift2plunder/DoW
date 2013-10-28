#!/usr/bin/perl -w
#
# Allows user to select a system and plot its trade history
#

use strict;

use dow;

my($Donor, $Resource);

$Donor = ProcessDowCommandline($Donor);

if ($#ARGV == -1) {
    GenerateSelection();
} elsif ($#ARGV == 0) {
    $Resource = $ARGV[0];
    $Resource =~ s/\\//g;
    GeneratePlot();
} else {
    usage();
}

PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: thres.cgi OR thres.cgi?Resource%20Name<p>\nWith no args, gives possible selections. With args, shows plot.");
}

sub GeneratePlot {
    add(DOW_HTML_Header($Donor, "DOW - Trade History of $Resource"));
    add("<img src=\"plottraderes.cgi?$Resource\">\n");
    add(DOW_HTML_Footer($Donor));
}

sub GenerateSelection {
    my($res, @res);
	
    add(DOW_HTML_Header($Donor, "DOW - Trade History By Resource"));
    add("<h1>Trade History by Resource</h1>\n");
    add("<table>\n");
    add(MakeHTMLTable(5, map { "<a href=\"thres.cgi?$_\">$_</a>&nbsp;&nbsp;&nbsp;" } SelectAll("select distinct resource from trade order by resource;")));
    add("</table>\n");
    add(DOW_HTML_Footer($Donor));
}

	
