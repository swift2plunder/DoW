#!/usr/bin/perl -w
#
# Show sightings in a system.
#

use strict;

use dow;

my ($Donor, $System);

$Donor = ProcessDowCommandline();

if ($#ARGV != 0) {
    usage();
}

$System = CanonicalizeSystem($ARGV[0]);
$System =~ s/\\//g;

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: sightings.cgi?System");
}

sub GeneratePage {
    my($sth, $row, $mstr, %turns, @turns, $req);

    if (! $Donor->{shiploc}) {
	herror("You must donate ship information to view ship information");
    }

    add(DOW_HTML_Header($Donor, "DOW Sightings in $System for $Donor->{ship}"));
    add("<h1>DOW Sightings at <a href=\"system.cgi?" . UncanonicalizeSystem($System) . "\">$System</a> for $Donor->{ship}</h1>\n");
    add("<table>\n");
    add("<tr><th>Pairings</th><th> &nbsp; </th><th>Trace Reports</th></tr>\n");
    add("<tr><td valign=top>");

    add("<table border>\n");
    add("<tr><th>Turn</th><th>Meeting</th></tr>\n");

    $sth = mydo("select * from meetings where system=? and donated=true order by turn desc;", $System);

    while ($row = $sth->fetchrow_hashref()) {
	$mstr = "<a href=\"shipsummary.cgi?$row->{ship1}\">$row->{ship1}</a>";
	if (isset($row, 'protected1')) {
	    $mstr .= " (protecting <a href=\"shipsummary.cgi?$row->{protected1}\">$row->{protected1}</a>)";
	}
	if (isset($row, 'ship2')) {
	    $mstr .= " meets <a href=\"shipsummary.cgi?$row->{ship2}\">$row->{ship2}</a>";
	    if (isset($row, 'protected2')) {
		$mstr .= " (protecting <a href=\"shipsummary.cgi?$row->{protected2}\">$row->{protected2}</a>)";
	    }
	} else {
	    $mstr .= " leftover";
	}
	add("<tr><td>$row->{turn}</td><td>$mstr</td></tr>\n");
	$turns{$row->{turn}} = 1;
    }
    add("</table>\n");
    $sth->finish();
    add("</td><td> &nbsp; &nbsp; &nbsp; </td><td valign=top>");

    add("<table border\n");
    add("<tr><th>Turn</th><th>Ship</th></tr>\n");

    $req = 'where system=?';
    @turns = keys(%turns);
    if ($#turns >= 0) {
	$req .= " and turn not in (" . join(", ", @turns) . ")";
    }

    $sth = mydo("select * from shiploc $req order by turn desc;", $System);

    while ($row = $sth->fetchrow_hashref()) {
	add("<tr><td>$row->{turn}</td><td><a href=\"shipsummary.cgi?$row->{ship}\">$row->{ship}</a></td></tr>\n");
    }
    $sth->finish();

    add("</table>\n");    


    add("</td></tr></table>\n");

    add(DOW_HTML_Footer($Donor));
}

sub isset {
    my($row, $str) = @_;
    return exists($row->{$str}) && defined($row->{$str}) && $row->{$str} !~ /^\s*$/;
}
