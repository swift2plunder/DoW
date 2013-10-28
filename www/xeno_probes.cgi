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

if (!$Donor->{xenoadmin}) {
    herror("This page is only available to the Xeno administrator");
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: xeno_probes.cgi");
}

sub GeneratePage {
    my($row, $sth, $turn);
    add(DOW_HTML_Header($Donor, "Probe Locations"));
    add("<h1>Probe Locations</h1>\n");
    $turn = SelectOne("select max(turn) from turnupdate;");

    # List existing probes first.

    add("<table border>\n");
    add("<tr><th>System</th><th>SN</th><th>Updated</th><th>Ship</th><th>Favour</th></tr>\n");
    $sth = mydo("select donors.ship, donors.donorid, probes.system, max(turn) as turn from probes, donors, systemviewed where xeno=true and probes.donorid=donors.donorid and systemviewed.system=probes.system group by donors.ship, donors.donorid, probes.system order by turn;");
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
	add("</tr>\n");
    }
    add("</table>\n");
    $sth->finish();    

    add("<p><hr><p>Non-Xenolgist DOW members have probes at ");
    add(join(", ", map { "<a href=\"system.cgi?" . UncanonicalizeSystem($_) . "\">$_</a>" } SelectAll("select distinct system from probes p, donors d where d.xeno=false and p.donorid=d.donorid order by system;")));

    # Now list members who have at least 65 favour and have already cast
    # Enlightenment and are at a system that: doesn't already has a probe,
    # doesn't have a starnet terminal, and isn't Olympus or Holiday.

    add("<p><hr><p>Listed below are xenos who have at least 65 favour, have already cast Enlightenment, and are at systems that: don't already have a probe, don't have a starnet terminals, and isn't Olympus or Holiday.<p>The \"probe\" column lists where they currently have a probe, if anywhere.\n");

    $sth = mydo("select * from donors d, favour f, skills s, shiploc l where d.xeno=true and d.donorid=f.donorid and f.turn=? and f.area='Science' and f.favour>65 and s.donorid=d.donorid and s.area='Science' and s.name='Enlightenment' and l.turn=f.turn and l.ship=d.ship order by favour desc;", $turn);
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
