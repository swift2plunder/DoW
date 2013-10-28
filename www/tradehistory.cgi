#!/usr/bin/perl -w
#
# Allows user to select a system/resource and plot its trade history
#

use strict;
use Getopt::Std;

use dow;

use vars qw($opt_s);

my($Orderby, $Donor, $System, $Resource);

$opt_s = 'sr';
getopts('s:') or usage();
$Orderby = GenerateOrderBy($opt_s, ('s' => 'system', 'r' => 'resource'));

$Donor = ProcessDowCommandline($Donor);

if ($#ARGV == -1) {
    GenerateSelection();
} elsif ($#ARGV == 1) {
    $System = CanonicalizeSystem($ARGV[0]);
    $Resource = $ARGV[1];
    $Resource =~ s/\\//g;
    GeneratePlot();
} else {
    usage();
}

PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: tradehistory.cgi OR tradehistory.cgi?System%20Name+Resource%20Name<p>\nWith no args, gives possible selections. With args, shows plot.");
}

sub GeneratePlot {
    add(DOW_HTML_Header($Donor, "DOW - Trade History of $Resource at $System"));
    add("<img src=\"plottrade.cgi?" . UncanonicalizeSystem($System) . "+$Resource\">\n");
    add(DOW_HTML_Footer($Donor));
}

sub GenerateSelection {
    my($sth, $row, $sa);

    add(DOW_HTML_Header($Donor, "DOW - Trade History"));
    add("<h1>Trade History</h1>\n");
    add("<table>\n");
    add("<tr>\n");
    $sa = GenerateSortArg($opt_s, 's');
    add(" <th align=left><a href=\"tradehistory.cgi?-s+$sa\">System</a></th>\n");
    $sa = GenerateSortArg($opt_s, 'r');
    add(" <th align=left><a href=\"tradehistory.cgi?-s+$sa\">Resource</a></th>\n");
    add(" <th> &nbsp; </th>\n");

    $sth = mydo("select distinct resource, system from trade $Orderby;");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr>\n");
	add(" <td><a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a>&nbsp;&nbsp;</td>\n");
	add(" <td><a href=\"res.cgi?$row->{resource}\">$row->{resource}</a>&nbsp;&nbsp;</td>\n");
	add(" <td><a href=\"tradehistory.cgi?" . UncanonicalizeSystem($row->{system}) . "+$row->{resource}\"><font size=\"-1\">Plot</font></a></td>\n");
    }
    add("</table>\n");
    $sth->finish();
    add(DOW_HTML_Footer($Donor));
}

	
