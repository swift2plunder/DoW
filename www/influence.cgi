#!/usr/bin/perl -w
#
# Show all influence with sortable columns
#

use strict;
use Getopt::Std;

use dow;

use vars qw($opt_s);

my($Donor, $Orderby);

$Donor = ProcessDowCommandline();

if (! $Donor->{influence}) {
    herror("You must provide influence information to view influence information");
}

$opt_s = 'Visparlt';
getopts('s:') or usage();

if ($#ARGV != -1) {
    usage();
}

$Orderby = GenerateOrderBy($opt_s, ('p' => 'ship',
				    'a' => 'area',
				    's' => 'system',
				    'r' => 'race',
				    'v' => 'votes',
				    'i' => 'influence',
				    'l' => 'location',
				    't' => 'turn'));
				    

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: influence.cgi");
}

sub GeneratePage {
    my($sth, $row, $sa);
    
    $sth = mydo("select * from (select distinct on (location) influence.*, aliens.area from influence, aliens where aliens.race=influence.race and donated=true order by location, turn desc) as orig $Orderby;");
    
    add(DOW_HTML_Header($Donor, "DOW - All Influence Data"));
    add("<h1>DOW - All Influence Data</h1>\n");
    add("<table><tr>");
    $sa = GenerateSortArg($opt_s, 'p');
    add("<th align=left><a href=\"influence.cgi?-s+$sa\">Ship</a></th>\n");

    $sa = GenerateSortArg($opt_s, 's');
    add("<th align=left><a href=\"influence.cgi?-s+$sa\">System</a></th>\n");

    $sa = GenerateSortArg($opt_s, 'r');
    add("<th align=left><a href=\"influence.cgi?-s+$sa\">Race</a></th>\n");

    $sa = GenerateSortArg($opt_s, 'a');
    add("<th align=left><a href=\"influence.cgi?-s+$sa\">Politics</a></th>\n");

    $sa = GenerateSortArg($opt_s, 'l');
    add("<th align=right><a href=\"influence.cgi?-s+$sa\">LocID</a></th>\n");

    $sa = GenerateSortArg($opt_s, 'v');
    add("<th align=right><a href=\"influence.cgi?-s+$sa\">Votes</a></th>\n");

    $sa = GenerateSortArg($opt_s, 'i');
    add("<th align=right><a href=\"influence.cgi?-s+$sa\">Influence</a></th>\n");

    $sa = GenerateSortArg($opt_s, 't');
    add("<th align=right><a href=\"influence.cgi?-s+$sa\">Updated</a></th>\n");
    add("</tr>\n");

    while ($row = $sth->fetchrow_hashref()) {
	add("<tr>\n");
	add(" <td><a href=\"shipsummary.cgi?$row->{ship}\">$row->{ship}</td>\n");
	add(" <td><a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . 
	    "\">$row->{system}</a></td>\n");
	add(" <td><a href=\"alien.cgi?$row->{race}\">$row->{race}</a></td>\n");
	add(" <td>$row->{area}</a></td>\n");
	add(" <td align=right>$row->{location}</td>\n");
	add(" <td align=right>$row->{votes}</td>\n");
	add(" <td align=right>$row->{influence}</td>\n");
	add(" <td align=right>$row->{turn}</td>\n");
	add("</tr>\n");
    }
    add("</table>");
    add(DOW_HTML_Footer($Donor));
}
