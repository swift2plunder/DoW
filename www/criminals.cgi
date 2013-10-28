#!/usr/bin/perl -w
#
# Show criminals
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
    herror("Usage: criminals.cgi");
}

sub GeneratePage {
    my($sth, $row, $turn);

    $turn = SelectOne("select max(turn) from criminals;");
    add(DOW_HTML_Header($Donor, "DOW Criminal Information for $Donor->{ship}"));
    add("<h1>DOW Criminal Information for $Donor->{ship}</h1>\n");
    add("<p>Note: According to a reliable source, there may be bugs in the criminal visibility. Please let me know if you notice problems with criminals.<p>");
    add("<p>Note 2: You can never capture criminals of rank higher than \"Heavy\" unless you've obtained their location from a lower level criminal. DOW does not track which criminals each member has seen, so you must check on your turn page when trying to capture anything other than \"Heavy\" criminals.<p>\n");
    $sth = mydo("select * from criminals where turn=? order by system;", $turn);
    add("<table border>\n");
    add("<tr><th>Race</th><th>Level</th><th>Location</th><th>System</th></tr>\n");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr>");
	add("<td>$row->{who}</td>");
	add("<td>$row->{level}</td>");
	add("<td>$row->{location}</td>");
	add("<td><a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a></td>");
	add("</tr>\n");
    }
    add("</table>");
    $sth->finish();
    add(DOW_HTML_Footer($Donor));
}

