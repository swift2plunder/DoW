#!/usr/bin/perl -w
#
# Show rogue bands
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
    herror("Usage: rogues.cgi");
}

sub GeneratePage {
    my($sth, $row, $turn, @easy, @hard, $astr, %skill);

    $turn = SelectOne("select max(turn) from rogues;");

    $skill{'Life Support'} = SelectOne("select lifesupportpercent from shipdata where donorid=? and turn=?;", $Donor->{donorid}, $turn);
    $skill{'Impulse'} = SelectOne("select impulsepercent from shipdata where donorid=? and turn=?;", $Donor->{donorid}, $turn);
    
    $sth = mydo("select * from rogues where turn=? order by field, system;", $turn);

    while ($row = $sth->fetchrow_hashref()) {
	$astr = "<tr>";
	$astr .= "<td>$row->{race}</td>\n";
	$astr .= "<td>$row->{field}</td>\n";
	$astr .= "<td>$row->{danger}% $row->{location}</td>\n";
	$astr .= "<td><a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a></td>\n";
	$astr .= "</tr>\n";

	if ($row->{danger} <= $skill{$row->{location}}) {
	    push(@easy, $astr);
	} else {
	    push(@hard, $astr);
	}
    }
    add(DOW_HTML_Header($Donor, "DOW Rogue Band Information for $Donor->{ship}"));
    add("<h1>DOW Rogue Band Information for $Donor->{ship}</h1>\n");
    add("<p>Go to <a href=\"roguemap.cgi\">Map View</a>.");
    add("<p><table border>\n");
    add("<tr><td valign=top><table border><tr><th colspan=4>Hirable Rogues Bands</th></tr>\n");
    add("<tr><th>Race</th><th>Field</th><th>Requires</th><th>System</th></tr>\n");
    add(join("\n", @easy));
    add("\n</table></td>");
    add("<td valign=top><table border><tr><th colspan=4>Unhirable Rogue Bands</th></tr>\n");
    add("<tr><th>Race</th><th>Field</th><th>Requires</th><th>System</th></tr>\n");
    add(join("\n", @hard));
    add("</table></td></tr></table>");
    add(DOW_HTML_Footer($Donor));
}
