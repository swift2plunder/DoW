#!/usr/bin/perl -w
#
# Show plague level at each system.
#

use strict;
use Getopt::Std;

use dow;

use vars qw($opt_s);

my($Donor);

$Donor = ProcessDowCommandline();
GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: plague.cgi?-ssp");
}

sub GeneratePage {
    my($sth, $row);
    add(DOW_HTML_Header($Donor, "Plague Levels"));
    add("<table border>\n");
    add("<tr><th>System</th><th>Plague Level</th><th>Turn Reported</th></tr>\n");
    $sth = mydo("select * from sysplagues order by level desc;");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr>\n");
	add(" <td><a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . 
	    "\">$row->{system}</a></td>\n");
	add(" <td>$row->{level}</td>\n");
	add(" <td>$row->{turn}</td>\n");
	add("</tr>\n");
    }
    add("</table>\n");
    add(DOW_HTML_Footer($Donor));
}
    
