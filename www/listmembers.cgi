#!/usr/bin/perl -w
#
# List all DOW members with a bit of associated info.
#
# Only to be used by me!

use strict;

use dow;

my $Donor = ProcessDowCommandline();

if (! $Donor->{admin}) {
    herror("This page only accessible by the administrator");
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub GeneratePage {
    my($sth, $row);

    add(DOW_HTML_Header($Donor, 'DOW Donors'));

    add("<h1>DOW Donors</h1>\n");

    add("<table border>\n");
    $sth = mydo("select * from donors where secreturl!= '' order by ship;");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr>\n");
	add("<td><a href=\"ms.cgi?-u+$row->{ship}\">$row->{ship}</a></td>\n");
	add("<td>$row->{donorid}</td>\n");
	add("<td>$row->{email}</td>\n");
	add("</tr>\n\n");
    }
    $sth->finish();
    add("</table>");

    add("<h1>DOW Ex-Donors</h1>\n");

    add("<table border>\n");
    $sth = mydo("select * from donors where secreturl = '' order by ship;");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr>\n");
	add("<td>$row->{ship}</td>\n");
	add("<td>$row->{donorid}</td>\n");
	add("<td>$row->{email}</td>\n");
	add("</tr>\n\n");
    }
    $sth->finish();
    add("</table>");




    add(DOW_HTML_Footer($Donor));
}
