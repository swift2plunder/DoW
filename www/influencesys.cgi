#!/usr/bin/perl -w
#
# Show influence for a system.
#

use strict;
use Getopt::Std;

use dow;

use vars qw($opt_t);

my($Donor, $System);

$Donor = ProcessDowCommandline();

if (! $Donor->{influence}) {
    herror("You must provide influence information to view influence information");
}

$opt_t = SelectOne("select max(turn) from turnupdate;");
getopts('t:') or usage();


if ($#ARGV != 0) {
    usage();
}

$System = CanonicalizeSystem($ARGV[0]);

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: influence.cgi?[-t+turn]+System");
}

sub GeneratePage {
    my($sth, $row);

    $sth = mydo("select distinct on (location) * from influence where system=? and donated=true order by location, turn desc;", 
		$System);
    
    add(DOW_HTML_Header($Donor, "DOW - Influences at $System"));
    add("<h1>DOW - Influences at <a href=\"system.cgi?" . UncanonicalizeSystem($System) . "\">$System</a></h1>\n");
    add("<table border>\n");
    add("<tr><th>Ship</th><th>Race</th><th>Politics</th><th>Location</th><th>Votes</th><th>Influence</th><th>Updated</th>\n");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr>\n");
	add(" <td><a href=\"influenceship.cgi?$row->{ship}\">$row->{ship}</a></td>");
	add(" <td>$row->{race}</td>\n");
	add(" <td>" . SelectOne("select area from aliens where race=?;", $row->{race}) . "</td>\n");
	if ($row->{votes} == 1) {
	    add(" <td>Colony $row->{location}</td>\n");
	} elsif ($row->{votes} == 8) {
	    add(" <td>Homeworld $row->{location}</td>\n");
	} else {
	    herror("Got neither 1 vote nor 8 votes. Shouldn't happen!");
	}
	add(" <td>$row->{votes}</td>\n");
	add(" <td>$row->{influence}</td>\n");
	add(" <td>$row->{turn}</td>\n");
	add("</tr>\n");
    }
    add("</table>\n");
    add(DOW_HTML_Footer($Donor));
}
