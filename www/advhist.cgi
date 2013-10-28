#!/usr/bin/perl -w
#
# Show historic adventure density of system.
#

use strict;

use dow;

my ($System, $Donor);

$Donor = ProcessDowCommandline();

if ($#ARGV != 0) {
    usage();
}

$System = CanonicalizeSystem($ARGV[0]);

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: advhist.cgi?SystemName\n<br> &nbsp; (e.g. system.cgi?S30)");
}

sub GeneratePage {
    my($sth, $row, $str, $tot, $n);
    add(DOW_HTML_Header($Donor, "DOW Adventure History at $System"));
    add("<h1>Adventure History at $System</h1>\n");
    $sth = mydo("select turn, count(*) from adventures where system=? group by turn order by turn desc;", $System);
    $str = '';
    $tot = 0;
    $n = 0;
    while ($row = $sth->fetchrow_hashref()) {
	$str .= "<tr><td>$row->{turn}&nbsp;&nbsp;&nbsp;&nbsp;</td><td align=right>$row->{count}</td></tr>\n";
	$tot += $row->{count};
	$n++;
    }
    if ($n > 0) {
	add(sprintf("Historic Average Number of Adventures: %0.1f\n<p>", $tot/$n));
	add("<hr><table><tr><th align=left>Turn</th><th align=right>#</th></tr>\n");
	add($str);
	add("</table>\n");
    } else {
	add("No adventures ever recorded!\n<p>");
    }
    add(DOW_HTML_Footer($Donor));
}

    
