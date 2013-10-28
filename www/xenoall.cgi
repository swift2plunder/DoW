#!/usr/bin/perl -w
#
# Institute of Xenology
#
# This page was used before the self admin system was instituted.
#

use strict;

use dow;

my $Donor = ProcessDowCommandline();

if (!$Donor->{admin}) {
    herror("Only for admin use");
}

my %Tasks = ( 'Ship' => 'Task',
	      'Another Ship' => 'Another task'
	      );


if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: xenoall.cgi");
}

sub GeneratePage {
    my($i, @xenos, @turns, $sth, $row);

    add(DOW_HTML_Header($Donor, "DOW - Institute of Xenology"));
    add("<h1>Institute of Xenology</h1>\n");
    if (!$Donor->{xeno}) {
	addxeno();
	add(DOW_HTML_Footer($Donor));
	return;
    }
    add("<h2><blink>READ THIS</blink></h2>\n");
    add("<p>The table below lists the current and upcoming Xenologist who will be required to perform a service for the Institute and the <em>turn of their last service</em> (you will never be required to perform a service sooner than 10 turns after that turn). If you would like to volunteer to perform a service prior to your turn, please either use the <a href=\"xenoself.cgi\">Self Administration</a> page, or email <a href=\"mailto:ninja\@janin.org\">A Mad Ninja</a>. If you don't, you will not get credit for the service!");
    add("<p><font size=\"+1\" color=F08080>You will receive an email on the turn you are required to perform the service.</font> The requested service listed in the table below assumes you will wait until your assigned turn.");

    @xenos = SelectAll("select ship from xeno_history group by ship order by max(turn) limit 8;");
    @turns = SelectAll("select max(turn) from xeno_history group by ship order by max(turn) limit 8;");

    add("<p>");
    add("<table>\n");
    add("<tr><th align=left>Last Service</th><th align=left>Ship</th><th align=left>Suggested Service</th></tr>\n");
    for ($i = 0; $i <= $#xenos; $i++) {
	add("<tr valign=top><td>$turns[$i]</td><td><a href=\"shipsummary.cgi?$xenos[$i]\">$xenos[$i]</a>&nbsp;&nbsp;&nbsp;&nbsp;</td><td>");
	if (exists($Tasks{$xenos[$i]})) {
	    add($Tasks{$xenos[$i]});
	} else {
	    add("&nbsp;");
	}
	add("</td></tr>\n");
    }
    add("</table>\n");
    add("<p><hr><p>Tasks performed by $Donor->{ship}:<p>");
    $sth = mydo("select * from xeno_history where ship=? order by turn desc;",
		$Donor->{ship});
    add("<table><tr><th align=right>Turn</th><th align=left>&nbsp;&nbsp;Action</th></tr>\n");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr><td align=right>$row->{turn}</td><td>&nbsp;&nbsp;$row->{action}</td></tr>\n");
    }
    add("</table>\n");
    add("<p><hr><p>\n");
    add("<a href=\"http://groups.yahoo.com/group/dow_xeno\">http://groups.yahoo.com/group/dow_xeno</a><br>\n");
    add("<a href=\"cs.cgi\">Combat Simulator</a><br>\n");
    add("Route Simulator (<a href=\"rsset.cgi\">set</a>) (<a href=\"rsresults.cgi\">results</a>)<br>\n");
    add("<a href=\"probes.cgi\">Probes</a> page.<br>\n");
    add("<a href=\"xenoself.cgi\">Self Administration</a> (select this the turn after you perform a service to record the service in the Institute logs).<br>\n");
    if ($Donor->{ship} eq "Mad Ninja") {
	add("<a href=\"xeno_admin.cgi\">Xeno Admin page</a><br>\n");
	add("<a href=\"xeno_terminals.cgi\">Xeno Terminals page</a>");
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
<p>If you are willing to be a Xeno, send email to <a href="mailto:ninja@janin.org">ninja@janin.org</a>.
<p>
EndOfXeno
     add($str);
}

