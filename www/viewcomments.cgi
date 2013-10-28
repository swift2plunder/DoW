#!/usr/bin/perl -w
#
# Show comments about a ship.
#
# I removed the bits that help obfuscate who's in DOW.
#

use strict;
use FileHandle;

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
    herror("Usage: viewcomments.cgi?Ship%20name");
}

sub GeneratePage {
    my($sth, $row, $ship);
    add(DOW_HTML_Header($Donor, "Comments on $Ship"));
    add("<h1>Comments on $Ship</h1>\n");
    addheader();
    add("<table><tr valign=top><th align=left>Score &nbsp; </th><th align=left>Comment</th><th>Turn</th><th>Who</th><th>&nbsp;</th></tr>\n");
    $sth = mydo("select * from shipcomments where ship=? order by dts desc;",
		$Ship);
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr valign=top>\n");
	add(" <td>$row->{score} &nbsp; &nbsp; </td>\n");
	add(" <td><table><tr><td>$row->{comment}</td></tr></table></td>\n");
	add("<td>$row->{turn}</td>\n");

	if (ExistsSelect("select * from donors where donorid=?;", $row->{donorid})) {
	    $ship = SelectOne("select ship from donors where donorid=?;",
			      $row->{donorid});
	    add("<td><a href=\"shipsummary.cgi?$ship\">$ship</a></td>\n");
	} else {
	    add("<td>id: $row->{donorid}</td>\n");
	}

	add(" <td><a href=\"removecomment.cgi?$row->{commentid}\"><font size=\"-1\">Delete</font></a></td>\n");

	add("</tr>\n");
    }
    add("</table>\n");
    add("<p><a href=\"entercomments.cgi?$Ship\">Enter comment</a> about $Ship.<p>\n");
    add(DOW_HTML_Footer($Donor));
}



sub addheader {
    my($turn, $race, $retturn);
    $turn = SelectOne("select max(turn) from turnupdate;");
    $race = RaceOfShip($Ship);
    if (ExistsSelect("select * from banned where ship=?;", $Ship)) {
	add("<font size=\"-1\">Banned from DOW: " . SelectOne("select description from banned where ship=?;", $Ship) . ".</font>\n");
    }
    if (!ExistsSelect("select * from activeships where ship=? and turn=?;", $Ship, $turn) && !defined($race)) {
	add("<font size=\"-1\">Retired");
	$retturn = SelectOne("select max(turn) from activeships where ship=?;",
			     $Ship);
	if (defined($retturn) && $retturn > 0) {
	    add(" on turn " . (1+$retturn));
	}
	add("</font>\n");
    }
}

