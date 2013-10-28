#!/usr/bin/perl -w
#
# Show ship location history.
#

use strict;

use dow;

my($Donor, $Ship);

$Donor = ProcessDowCommandline();

if ($#ARGV != 0) {
    usage();
}

$Ship = $ARGV[0];
$Ship =~ s/\\//g;

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: shiploc.cgi?Ship%20name");
}

sub GeneratePage {
    my($sth, $row, $mstr, %turns);
    if (! $Donor->{shiploc}) {
	herror("You must donate ship location information to view ship location information");
    }
    
    add(DOW_HTML_Header($Donor, "DOW $Ship Location Information"));
    add("<h1>DOW <a href=\"shipsummary.cgi?$Ship\">$Ship</a> Location Information</h1>\n");

    add("Go to <a href=\"shiplocmap.cgi?$Ship\">Map View</a>.<p><hr><p>\n");
    
    add("<table>\n");
#    add("<tr><th>Pairings</th><th> &nbsp; </th><th>Trace Reports</th></tr>\n");
    add("<tr><th>Pairings</th><th> &nbsp; </th></tr>\n");
    add("<tr><td valign=top>");

    $sth = mydo("select * from meetings where (ship1=? or ship2=? or protected1=? or protected2=?) and donated=true and system != 'Holiday Planet' order by turn desc", $Ship, $Ship, $Ship, $Ship);

    add("<table border>\n");
    add("<tr><th>System</th><th>Turn</th><th>Meeting</th></tr>\n");
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
	add("<tr><td><a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a></td><td>$row->{turn}</td><td>$mstr</td></tr>\n");
	$turns{$row->{turn}} = 1;
    }
    add("</table>");
    $sth->finish();

    add("</td><td> &nbsp; &nbsp; &nbsp; </td><td valign=top>");
    
    $sth = mydo("select * from shiploc where ship=? and turn not in (" . join(", ", keys(%turns)) . ") and donated=true and system !='Holiday Planet' order by turn desc;", $Ship);

    add("</td></tr></table>\n");
    add(DOW_HTML_Footer($Donor));
    $sth->finish();
}

sub isset {
    my($row, $str) = @_;
    return exists($row->{$str}) && defined($row->{$str}) && $row->{$str} !~ /^\s*$/;
}
