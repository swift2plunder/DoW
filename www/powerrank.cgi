#!/usr/bin/perl -w
#
# Show power rank of all ships
#

use strict;
use Getopt::Std;

use dow;

use vars qw($opt_s);

my($Donor, $Orderby);

$Donor = ProcessDowCommandline();

if (! $Donor->{shipconfig}) {
    herror("You must provide ship config information to view powerrank list.");
}

$opt_s = 'Ps';
getopts('s:') or usage();

if ($#ARGV != -1) {
    usage();
}

$Orderby = GenerateOrderBy($opt_s, ('s' => 'ship',
				    'p' => 'powerrank'));

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: powerrank.cgi");
}

sub GeneratePage {
    my($sth, $row, $sa);
    $sth = mydo("select p1.* from powerrank p1, (select ship, max(turn) from powerrank group by ship) p2 where p1.ship=p2.ship and p1.turn=p2.max $Orderby;");
    
    add(DOW_HTML_Header($Donor, "Power Ranks"));
    add("<h1>Power Ranks</h1>\n");
    add("<table><tr>");

    $sa = GenerateSortArg($opt_s, 's');
    add("<th align=left><a href=\"powerrank.cgi?-s+$sa\">Ship</a></th>\n");

    $sa = GenerateSortArg($opt_s, 'p');
    add("<th align=right><a href=\"powerrank.cgi?-s+$sa\">Rank</a></th>\n");

    add("<th align=right>Updated</th>\n");
    add("</tr>\n");

    while ($row = $sth->fetchrow_hashref()) {
	add("<tr>\n");
	add(" <td><a href=\"shipsummary.cgi?$row->{ship}\">$row->{ship}</td>\n");
	add(" <td align=right>$row->{powerrank}</td>\n");
	add(" <td align=right>$row->{turn}</td>\n");
	add("</tr>\n");
    }
    add("</table>");
    add(DOW_HTML_Footer($Donor));
}

	

    
