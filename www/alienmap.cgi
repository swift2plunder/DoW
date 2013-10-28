#!/usr/bin/perl -w
#
# Show map of alien enemies
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
    herror("Usage: alienmap.cgi");
}

sub GeneratePage {
    my($sth, $row, $turn, @friends, @enemies);

    $turn = SelectOne("select max(turn) from enemies where donorid=?;", 
		      $Donor->{donorid});

    $sth = mydo("select * from aliens;");

    while ($row = $sth->fetchrow_hashref()) {
	if (ExistsSelect("select who from enemies where donorid=? and who=? and turn=?;", 
			 $Donor->{donorid}, $row->{race}, $turn)) {
	    push(@enemies, $row->{system});
	} else {
	    push(@friends, $row->{system});
	}
    }
    add(DOW_HTML_Header($Donor, "DOW Alien Relations for $Donor->{ship}"));
    add("<h1>DOW Alien Relations for $Donor->{ship}</h1>");
    add("<p>Go to <a href=\"aliens.cgi\">List View</a>.");
    add("<hr>");
    add(MakeMap($Donor->{ship}, \@enemies, \@friends));
    add("<hr>");
    add("<img src=\"bigred.gif\">Enemies<br>\n");
    add("<img src=\"biggreen.gif\">Not Enemies<br>\n");
    add(DOW_HTML_Footer($Donor));
}
