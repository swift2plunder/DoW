#!/usr/bin/perl -w
#
# Show trade resource
#

use strict;

use dow;

my($Donor, $Res);

$Donor = ProcessDowCommandline();

if ($#ARGV != 0) {
    usage();
}

$Res = $ARGV[0];
$Res =~ s/\\//g;

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: res.cgi?res<br> &nbsp; Show trade resource res");
}

sub GeneratePage {
    my($syssth, $sysrow, $ressth, $resrow, $sth, $row, $shipsystem, $sysurl, $shipsysurl, $turn);
    my($nres, $npods, @factory, @colonies);

    add(DOW_HTML_Header($Donor, "DOW Trade Resources - $Res Information for $Donor->{ship}"));
    add("<h1>DOW Trade Resources - $Res Information for $Donor->{ship}</h1>\n");

    $turn = SelectOne("select max(turn) from turnupdate where donorid=?;", $Donor->{donorid});
    $shipsystem = SelectOne("select system from shiploc where ship=? and turn=?;", $Donor->{ship}, $turn);

    $shipsysurl = "<a href=\"system.cgi?" . UncanonicalizeSystem($shipsystem) . "\">$shipsystem</a>";

    $sth = mydo("select * from factories where resource=?;", $Res);
    $row = $sth->fetchrow_hashref();
    $sth->finish();
    if (!defined($row)) {
	herror("Could not find factory for resource $Res.");
    }
    $sysurl = "<a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a>";
    push(@factory, $row->{system});

    add("Produced at $sysurl for \$$row->{cost}");
    add(" (jump cost from $shipsysurl to $sysurl is \$" . 
	GetJumpCost($Donor->{donorid}, $turn, $shipsystem, $row->{system}) . ")");
    $nres = SelectOne("select sum(n) from pods where donorid=? and turn=? and resource=?;",
		      $Donor->{donorid}, $turn, $Res);
    if (!defined($nres) || $nres !~ /[0-9]+/) {
	add("<p>You are not carrying any $Res.");
    } else {
	$npods = SelectOne("select count(n) from pods where donorid=? and turn=? and resource=?;",
			   $Donor->{donorid}, $turn, $Res);
	if (!defined($npods) || $npods !~ /[0-9]+/) {
	    herror("Mismatch pods npods in res.cgi. This shouldn't happen.");
	}
	add("<p>You are carrying $nres $Res in $npods pod");
	if ($npods > 1) {
	    add("s");
	}
	add(".");
    }
    add("<p><a href=\"colonies.cgi?$Res\">Colony Details</a>\n");
    add("<hr><table>\n");
    add("<tr><th align=\"left\">System</th><th align=\"left\">&nbsp;&nbsp;&nbsp;Updated</th><th align=\"right\">&nbsp;&nbsp;Price</th><th align=right> &nbsp; &nbsp; Jump</th><th>(from $shipsysurl)</th></tr>\n");
    
    $syssth = mydo("select distinct system, max(turn) as turn from trade where resource=? group by system;", $Res);

    $ressth = myprep("select price from trade where system=? and resource=? and turn=?;");

    while ($sysrow = $syssth->fetchrow_hashref()) {
	push(@colonies, $sysrow->{system});
	myex($ressth, $sysrow->{system}, $Res, $sysrow->{turn});
	while ($resrow = $ressth->fetchrow_hashref()) {
	    add("<tr>");
	    add("<td><a href=\"system.cgi?" . UncanonicalizeSystem($sysrow->{system}) . "\">$sysrow->{system}</a></td>");
	    add("<td align=\"left\">&nbsp;&nbsp;&nbsp;$sysrow->{turn}</td>\n");
	    add("<td align=\"right\">$resrow->{price}</td>\n");
	    add("<td align=\"right\"> &nbsp; &nbsp; " . GetJumpCost($Donor->{donorid}, $turn, $shipsystem, $sysrow->{system}) . "</td>\n");
	    add("</tr>\n");
	}
    }
    add("</table>\n");
    $ressth->finish();    
    $syssth->finish();
    add("<hr><p>");
    add(MakeMap($Donor->{ship}, \@colonies, \@factory));
    add(DOW_HTML_Footer($Donor));
}
