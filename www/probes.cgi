#!/usr/bin/perl -w
#
# Show who/what/where of probes.
#

use strict;

use dow;

my($Donor);

$Donor = ProcessDowCommandline();

if ($#ARGV != -1) {
    usage();
}

# Removed for anonymity
if (!$Donor->{admin}) {
    herror("This page is only available to the DOW administrator");
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: probes.cgi");
}

sub GeneratePage {
    my($row, $sth, $turn);
    add(DOW_HTML_Header($Donor, "Probe Locations"));
    add("<h1>Probe Locations</h1>\n");
    $turn = SelectOne("select max(turn) from turnupdate;");

    # List existing probes first.

    add("<table border>\n");
    add("<tr><th>System</th><th>SN</th><th>Updated</th><th>Ship</th><th>Favour</th><th>Xeno</th>\n");
    $sth = mydo("select d.ship, d.donorid, p.system, max(v.turn) as turn from probes p, donors d, systemviewed v, shiploc l where p.donorid=d.donorid and v.system=p.system and l.ship=d.ship and l.system!='Holiday Planet' and l.turn=? group by d.ship, d.donorid, p.system order by turn;", $turn);
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr>\n");
	add(" <td><a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a></td>\n");
	if (ExistsSelect("select * from sysstarnet where system=?;", $row->{system})) {
	    add(" <td>SN&nbsp;&nbsp;</td>\n");
	} else {
	    add(" <td>&nbsp;&nbsp;</td>\n");
	}
	add("<td>$row->{turn}&nbsp;&nbsp;</td>\n");

	add(" <td><a href=\"shipsummary.cgi?$row->{ship}\">$row->{ship}</a>&nbsp;&nbsp;</td>\n");
	add("<td>" . SelectOne("select favour from favour where area='Science' and donorid=? and turn=?;", $row->{donorid}, $turn) . "&nbsp;&nbsp;</td>\n");
	if (SelectOne("select xeno from donors where donorid=?;", $row->{donorid})) {
	    add("<td>Yes</td>\n");
	} else {
	    add("<td>No</td>\n");
	}
	add("</tr>\n");
    }
    add("</table>\n<p><hr><p>\n");
    $sth->finish();    

    # Now list members who have at least 65 favour and have already cast
    # Enlightenment and are at a system that: doesn't already has a probe,
    # doesn't have a starnet terminal, and isn't Olympus or Holiday.

    $sth = mydo("select * from donors d, favour f, skills s, shiploc l where d.donorid=f.donorid and f.turn=? and f.area='Science' and f.favour>65 and s.donorid=d.donorid and s.area='Science' and s.name='Enlightenment' and l.turn=f.turn and l.ship=d.ship order by favour desc;", $turn);
    add("<table border>\n");
    add("<tr><th>Ship</th><th>Favour</th><th>Location</th><th>Probe</th></tr>\n");
    while ($row = $sth->fetchrow_hashref()) {
	next if (ExistsSelect("select * from probes where system=?;", $row->{system}));
	next if ($row->{system} eq 'Holiday Planet');
	next if ($row->{system} eq 'Olympus');
	next if (ExistsSelect("select * from sysstarnet where system=?;", $row->{system}));
	add("<tr>\n");
	add("<td><a href=\"shipsummary.cgi?$row->{ship}\">$row->{ship}</a>&nbsp;&nbsp;</td>\n");
	add("<td>$row->{favour}&nbsp;&nbsp;</td>\n");
	add(" <td><a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a>&nbsp;&nbsp;</td>\n");

	if (ExistsSelect("select * from probes where donorid=?;", $row->{donorid})) {
	    add("<td>" . SelectOne("select system from probes where donorid=?", $row->{donorid}) . "&nbsp;</td>\n");
	} else {
	    add("<td>&nbsp;</td>\n");
	}
	
	add("</tr>\n");
    }
    $sth->finish();
    add("</table>\n");

    add(DOW_HTML_Footer($Donor));
}
