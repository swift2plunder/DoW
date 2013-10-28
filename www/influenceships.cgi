#!/usr/bin/perl -w
#
# Show all players influence
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

$opt_s = 'Vs';
getopts('s:') or usage();

if ($#ARGV != -1) {
    usage();
}

$Orderby = GenerateOrderBy($opt_s, ('s' => 'ship',
				    'v' => 'sum'));
				    

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: influenceships.cgi");
}

sub GeneratePage {
    my($sth, $row, $sa);

    $sth = mydo("select ship, sum(votes) from (select distinct on (location) ship, votes from influence where donated=true order by location, turn desc) as orig group by ship $Orderby;");

    add(DOW_HTML_Header($Donor, "DOW - Influence by Ship"));
    add("<h1>DOW - Influence By Ship</h1>\n");
    add("<table><tr>");
    $sa = GenerateSortArg($opt_s, 's');
    add("<th align=left><a href=\"influenceships.cgi?-s+$sa\">Ship</a></th>\n");
    $sa = GenerateSortArg($opt_s, 'v');
    add("<th align=right><a href=\"influenceships.cgi?-s+$sa\">Votes</a></th>\n");
    add("</tr>\n");

    while ($row = $sth->fetchrow_hashref()) {
	add("<tr>\n");
	add(" <td><a href=\"influenceship.cgi?$row->{ship}\">$row->{ship}</td>\n");
	add(" <td>$row->{sum}</td>\n");
	add("</tr>\n");
    }
    add("</table>");
    add(DOW_HTML_Footer($Donor));
}
