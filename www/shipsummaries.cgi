#!/usr/bin/perl -w
#
# List all ships for which we have info and user can access. 
# Link to ship summary.
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
    herror("Usage: shipsummaries.cgi");
}

sub GeneratePage {
    my($turn, @ships, @aliens, @retired);
    
    $turn = SelectOne("select max(turn) from turnupdate;");

    @ships = map { "<a href=\"shipsummary.cgi?$_\">$_</a>" } SelectAll("select ship from allships where turn=? and type=?;", $turn, "Player");

    @aliens = map { "<a href=\"shipsummary.cgi?$_\">$_</a>" } SelectAll("select ship from allships where turn=? and type=?;", $turn, "Alien");

    @retired = map { "<a href=\"shipsummary.cgi?$_\">$_</a>" } SelectAll("select ship from allships where turn=? and type=?;", $turn, "Retired");

    add(DOW_HTML_Header($Donor, "DOW Ship Summaries for $Donor->{ship}"));
    add("<h1>DOW Ship Summaries for $Donor->{ship}</h1>\n");
    add("<table boder>\n");
    add(MakeHTMLTable(4, @ships, ' &nbsp; ', @aliens, ' &nbsp; ', '<em>Retired Ships</em>', @retired));
    add("</table>");
    add(DOW_HTML_Footer($Donor));
}
