#!/usr/bin/perl -w
#
# Show trade resource
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
    herror("Usage: allres.cgi");
}

sub GeneratePage {
    my($sth, $row, $sres, @res, $nres, $turn);

    $turn = SelectOne("select max(turn) from turnupdate where donorid=?;", $Donor->{donorid});

    add(DOW_HTML_Header($Donor, "DOW - Trade Resources"));
    add("<h1>DOW - Trade Resources</h1>\n");
    add("<p>Lists all trade resources and the number you are currently carrying.<p><hr><p>");

    $sth = mydo("select * from factories;");
    while ($row = $sth->fetchrow_hashref()) {
	$sres = $row->{resource};
	$nres = SelectOne("select sum(n) from pods where donorid=? and turn=? and resource=?;",
			  $Donor->{donorid}, $turn, $sres);
	if (!defined($nres) || $nres !~ /[0-9]+/ || $nres == 0) {
	    $nres = ' &nbsp; &nbsp; ';
	}
	push(@res, "<font size=\"-1\">$nres</font> <a href=\"res.cgi?$sres\">$row->{resource}</a> &nbsp; &nbsp; ");
    }
    $sth->finish();
    add("<table>\n");
    add(MakeHTMLTable(3, @res));
    add("</table>\n");
    add("<p>");
    $sth = mydo("select * from medicine where ship=? and turn=?;", $Donor->{ship}, $turn);
    $row = $sth->fetchrow_hashref();
    if (defined($row) && exists($row->{system}) && defined($row->{system})) {
	add("Holding Medicine worth \$$row->{value} at <a href=\"system.cgi?" .
	    UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a>\n");
    }
    $sth->finish();
    add(DOW_HTML_Footer($Donor));
}
