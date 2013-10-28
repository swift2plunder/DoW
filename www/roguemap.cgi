#!/usr/bin/perl -w
#
# Show map of rogue bands
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
    herror("Usage: roguemap.cgi");
}

sub GeneratePage {
    my($sth, $row, $turn, @easy, @hard, %skill);

    $turn = SelectOne("select max(turn) from rogues;");

    $skill{'Life Support'} = SelectOne("select lifesupportpercent from shipdata where donorid=? and turn=?;", $Donor->{donorid}, $turn);
    $skill{'Impulse'} = SelectOne("select impulsepercent from shipdata where donorid=? and turn=?;", $Donor->{donorid}, $turn);
    
    $sth = mydo("select * from rogues where turn=?;", $turn);

    while ($row = $sth->fetchrow_hashref()) {
	if ($row->{danger} <= $skill{$row->{location}}) {
	    push(@easy, $row->{system});
	} else {
	    push(@hard, $row->{system});
	}
    }
    $sth->finish();
    add(DOW_HTML_Header($Donor, "DOW Rogue Band Information for $Donor->{ship}"));
    add("<h1>DOW Rogue Band Information for $Donor->{ship}</h1>\n");
    add("<p>Go to <a href=\"rogues.cgi\">List View</a>.");
    add("<hr>");
    add(MakeMap($Donor->{ship}, \@easy, \@hard));
    add("<hr>");
    add("<img src=\"bigred.gif\">Hireable Rogue Bands<br>\n");
    add("<img src=\"biggreen.gif\">Unhireable Rogue Bands<br>\n");
    add(DOW_HTML_Footer($Donor));
}
