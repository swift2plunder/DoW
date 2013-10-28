#!/usr/bin/perl -w
#
# Institute of Xenology
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
    herror("Usage: xeno.cgi");
}

sub GeneratePage {
    my($sth, $row, $turn, $maxturn);

    $turn = SelectOne("select max(turn) from turnupdate;");

    add(DOW_HTML_Header($Donor, "DOW - Institute of Xenology"));
    add("<h1>Institute of Xenology</h1>\n");
    if (!$Donor->{xeno}) {
	addxeno();
	add(DOW_HTML_Footer($Donor));
	return;
    }

    if ($Donor->{admin}) {
	GenerateAdmin();
    }

    if ($Donor->{xenoadmin}) {
	GenerateXenoAdmin();
    }

    $maxturn = SelectOne("select max(turn) from xeno_history where ship=?;", $Donor->{ship});
    add("<p><hr><p><font size=\"+1\">\n");
    if ($turn > 15 + $maxturn) {
	add("It is your turn to perform a task. If you are unable to decide on a task, either post to the <a href=\"forumread.cgi?-f+xeno\">Xeno</a> forum on DOW or email me at <a href=\"mailto:ninja\@janin.org\">ninja\@janin.org</a>.\n");
    } elsif ($turn > 10 + $maxturn) {
	add("Your turn to perform a task is approaching (" . (15 - $turn + $maxturn) . " turns). Please consider volunteering for a service.\n");
    } else {
	add("It will be your turn to perform a task in about " . (15 - $turn + $maxturn) . " turns. Feel free to volunteer before then, though!\n");
    }

    add("<p><hr><p>Tasks performed by $Donor->{ship}:<p>");
    $sth = mydo("select * from xeno_history where ship=? order by turn desc;",
		$Donor->{ship});
    add("<table><tr><th align=right>Turn</th><th align=left>&nbsp;&nbsp;Action</th></tr>\n");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr><td align=right>$row->{turn}</td><td>&nbsp;&nbsp;$row->{action}</td></tr>\n");
    }
    add("</table>\n");
    $sth->finish();

    add("<p><hr><p>\n");
    add("<a href=\"cs.cgi\">Combat Simulator</a><br>\n");
    add("Route Simulator (<a href=\"rsset.cgi\">set</a>) (<a href=\"rsresults.cgi\">results</a>)<br>\n");
    add("<a href=\"xenoself.cgi\">Self Administration</a> (select this the turn after you perform a service to record the service in the Institute logs).<br>\n");
    add("<a href=\"forumread.cgi?-f+xeno\">Forum</a>.<br>\n");
    if ($Donor->{xenoadmin}) {
	add("<a href=\"xeno_admin.cgi\">Xeno Admin page</a><br>\n");
	add("<a href=\"xeno_terminals.cgi\">Xeno Terminals page</a>");
	add("<a href=\"xeno_probes.cgi\">Xeno Probes page</a>");
    }
    add(DOW_HTML_Footer($Donor));
}

sub addxeno {
    my($str);
    $str = <<'EndOfXeno';
<p>This page is for the Institute of Xenology. If you are seeing this message, 
you are NOT an official member. Official members see another page.

<p>Xenologists take turns providing extra information for DOW. The sorts of
services Xenos provide include:
<ul>
<li>Jumping to a nearby seldomly visited system
<li>Accessing a terminal
<li>Casting "Deploy Probe"
<li>Casting "Report from Probe"
<li>Casting "Report from All Terminals"
<li>Casting "Discover Adventure"
<li>Casting "Trace X", where X is an enemy (e.g. UPF, Orange, BSL, etc)
<li>Casting "View X"
<li>Etc.
</ul>
<p>Members are expected to perform a service once every 15 turns or so.

<p>Additionally, members are expected to act in the best interests of
DOW. You should act in ways that encourage people to join DOW, and
generally oppose DOW enemies. I do not demand active opposition, since
that's not always compatible with good tactics and strategy. But I do
demand no active support.

<p>Membership in the Institute is totally at my discretion. If I find you
violating the above, you may or may not receive warning before you are
dropped from the roles of the Institute.

<p>Members of the Institute gain two privileges. They can run the trade route simulator
and they can simulate combat vs. the ship they are paired with.
<p>If you are willing to be a Xeno, send email to <a href="mailto:ninja@janin.org">ninja@janin.org</a>.
<p>
EndOfXeno
     add($str);
}


sub GenerateXenoAdmin {
}

sub GenerateAdmin {
    my($sth, $row, $turn, $sys);
    $turn = SelectOne("select max(turn) from turnupdate;");

    $sth = mydo("select d.donorid, h.ship, max(h.turn), l.system, d.email, f.favour from favour f, xeno_history h, donors d, shiploc l where l.system!='Holiday Planet' and f.area='Science' and f.donorid=d.donorid and f.turn=l.turn and d.ship=h.ship and d.xeno and l.ship=d.ship and l.turn=? group by d.donorid, h.ship, l.system, f.favour, d.email having max(h.turn)<=? order by 3 limit 15;", $turn, $turn-10);

    add("<p>Admin Data<p><table>\n");
    add("<tr><th align=left>Last<br>Service</th><th align=left>Ship</th><th align=left>email</th><th align=left>Location</th><th align=left>Fav</th><th align=left><a href=\"xeno_probes.cgi\">Probe</a></th><th>&nbsp;</th></tr>\n");

    while ($row = $sth->fetchrow_hashref()) {
	add("<tr valign=top>\n");
	add("<td>$row->{max}</td>\n");
	add("<td><a href=\"shipsummary.cgi?$row->{ship}\">$row->{ship}</a></td>");
	add("<td>$row->{email}</td>\n");
	add("<td><a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a></td>\n");
	add("<td>$row->{favour}</td>\n");
	
	if (ExistsSelect("select * from probes where donorid=?;", $row->{donorid})) {
	    $sys = SelectOne("select system from probes where donorid=?;",
			     $row->{donorid});
	    add("<td><a href=\"system.cgi?" . UncanonicalizeSystem($sys) . "\">$sys</a></td>\n");
	} else {
	    add("<td>None</td>\n");
	}
	add("<td><a href=\"xenoself.cgi?-u+$row->{ship}\"><font size=\"-1\">self</font></a></td>\n");
	add("</tr>\n");
    }
    add("</table>\n");
}
