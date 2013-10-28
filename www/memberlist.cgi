#!/usr/bin/perl -w
#
# Originally, this listed all DOW members. It was completely removed for
# a while, and then replaced with this joke page. I don't think anybody
# noticed. :-(
#

use strict;

use dow;

my($Donor);

$Donor = ProcessDowCommandline();

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: memberlist.cgi");
}


sub GeneratePageFake {
    my($sth, $row, $val, $qship);
    $qship = DBQuote($Donor->{ship});
    add(DOW_HTML_Header($Donor, "DOW Membership List"));
    add("<h1>DOW Membership List</h1>\n");
    add("Please remember that sharing DOW information with non-members is forbidden. This prohibition includes the membership list.<p><hr>\n");

    # Ooh, I'm SO clever...
    $val = sprintf("%1.3f", $Donor->{donorid} / 1000.0);
    mydo("select setseed($val);");

    add(join(', ', map { "<a href=\"shipsummary.cgi?$_\">$_</a>" } SelectAll("select ship from (select distinct ship from ((select ship from activeships where ship not in (select ship from banned) and turn=(select max(turn) from turnupdate) order by random() limit 60) UNION select $qship) s1) s2 order by random();")));
    add(DOW_HTML_Footer($Donor));
}
