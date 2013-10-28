#!/usr/bin/perl -w
#
# Show ordered list of out of date homeworlds.
#
# Removed some stuff that restricted access to a few Xeno members.
#

use strict;
use dow;

my($Donor);

$Donor = ProcessDowCommandline();

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub GeneratePage {
    my($sth, $row);
    add(DOW_HTML_Header($Donor, "Out of Date Homewords"));
    add("<p>Lists homeworlds and when they were last visited by a DOW member. This can leak DOW membership inforamtion, so it's only available to selected ships. Please don't share data.\n");
    add("<table><tr><th>System</th><th>Turn</th></tr>\n");
    $sth = mydo("select max(turn) as turn, l.system from shiploc l, donors d, aliens a where a.system=l.system and l.ship=d.ship group by l.system order by turn;");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr><td>$row->{system}</td><td>$row->{turn}</td></tr>\n");
    }
    add("</table>\n");
    add(DOW_HTML_Footer($Donor));
}
