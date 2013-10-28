#!/usr/bin/perl -w
#
# Show list of various things of interest.
#

use strict;

use dow;

my $Donor = ProcessDowCommandline();

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: locs.cgi");
}

sub GeneratePage {
    my($sth, $row);

    $sth = mydo("select distinct item from statics order by item;");
    add(DOW_HTML_Header($Donor, "DOW - Other Locations of Interest"));
    add("<h1>DOW - Other Locations of Interest</h1>\n");
    add("<table>\n");
    while($row = $sth->fetchrow_hashref()) {
	add("<tr>\n");
	add(" <td align=right>$row->{item}</td>\n");
	add(" <td> &nbsp; <a href=\"loc.cgi?$row->{item}\">List View</a> &nbsp; </td>");
	add(" <td><a href=\"loc.cgi?-m+$row->{item}\">Map View</a></td>");
	add("</tr>\n\n");
    }
    $sth->finish();
    add("</table>\n");
    # DOW members voted for popcorn not to be listed.
    if ($Donor->{admin}) {
	add("<p>\n");
	$row = SelectOneRowAsHash("select * from popcorn order by turn desc limit 1;");
	if (SelectOne("select max(turn) from turnupdate;") == $row->{turn}) {
	    add("The Popcorn source is <a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a>:");
	} else {
	    add("The Popcorn source was <a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a> on turn $row->{turn}:");
	}
	add("   Impulse " . $row->{impulse} . "%");
	add("   Sensor " . $row->{sensor} . "%");
	add("   Shield " . $row->{shield} . "%");
	add("<br>\n");
    }	    

    add(DOW_HTML_Footer($Donor));
}
