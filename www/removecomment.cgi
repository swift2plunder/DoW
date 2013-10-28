#!/usr/bin/perl -w
#
# Remove a ship.
#

use strict;
use FileHandle;

use dow;

my($Donor, $CommentID);

$Donor = ProcessDowCommandline();

if ($#ARGV != 0) {
    usage();
}

$CommentID = $ARGV[0];

if ($CommentID !~ /^\s*[0-9]+\s*$/) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: removecomment.cgi?CommentID (a number)");
}

sub GeneratePage {
    my($sth, $row);

    $sth = mydo("select * from shipcomments where commentid=?;", $CommentID);
    $row = $sth->fetchrow_hashref();
    if (!defined($row)) {
	herror("Couldn't find commentid $CommentID");
    }
    if ($row->{donorid} != $Donor->{donorid}) {
	herror("Only the person who made the comment may delete it.");
    }

    add(DOW_HTML_Header($Donor, "DOW - Removing Comment"));
    add("<h1>Removing Comment</h1>\n");
    add("<p>The following comment has been removed.<p>");
    add("<table><tr><th>Turn</th><th>Ship</th><th>Score</th><th>Comment</th></tr>\n");
    add("<tr>\n");
    add(" <td>$row->{turn}</td>\n");
    add(" <td><a href=\"shipsummary.cgi?$row->{ship}\">$row->{ship}</a></td>\n");
    add(" <td>$row->{score}</td>\n");
    add(" <td><table><tr><td>$row->{comment}</td></tr></table></td>\n");
    add("</tr>\n");
    add("</table>\n");
    $sth->finish();
    add(DOW_HTML_Footer($Donor));
    mydo("delete from shipcomments where commentid=?;", $CommentID);
}
