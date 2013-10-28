#!/usr/bin/perl -w
#
# Map of all DOW members.
#

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
    my($sth, $row, @sys, $turn, @many, @single);

    add(DOW_HTML_Header($Donor, 'DOW Donors'));
    add("<h1>DOW Donors</h1>\n");
    $turn = SelectOne("select max(turn) from turnupdate;");

    $sth = mydo("select system, count(system) from donors, shiploc where shiploc.ship=donors.ship and turn=? group by system;", $turn);

    while ($row = $sth->fetchrow_hashref()) {
	if ($row->{count} > 1) {
	    push(@many, $row->{system});
	} else {
	    push(@single, $row->{system});
	}
    }
    $sth->finish();

    add(MakeMap($Donor->{ship}, \@many, \@single));
    add(DOW_HTML_Footer($Donor));
}
