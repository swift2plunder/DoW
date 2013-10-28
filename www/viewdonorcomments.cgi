#!/usr/bin/perl -w
#
# Show comments by a donor
#

use strict;
use FileHandle;

use dow;

my($Donor, $ByDonor);

$Donor = ProcessDowCommandline();

if ($#ARGV != 0) {
    usage();
}

$ByDonor = $ARGV[0];
$ByDonor =~ s/\\//g;

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: viewdonorcomments.cgi?Donor%20Ship%20name");
}

sub GeneratePage {
    my($lab, $sth, $row);
    add(DOW_HTML_Header($Donor, "DOW Member Comments by $ByDonor"));
    add("<h1>DOW Member Comments by $ByDonor</h1>\n");
    add("<table><tr valign=top><th align=left>Turn &nbsp; &nbsp; </th><th align=left>Ship</th><th align=right>Score &nbsp; </th><th align=left>Comment</th><th>&nbsp;</th></tr>\n");
    $sth = mydo("select shipcomments.* from shipcomments, donors where donors.label=? and donors.donorid=shipcomments.donorid order by dts desc;", $ByDonor);
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr valign=top>\n");
	add(" <td>$row->{turn} &nbsp; &nbsp; </td>\n");
	add(" <td><a href=\"shipsummary.cgi?$row->{ship}\">$row->{ship}</a> &nbsp; &nbsp; </td>\n");
	add(" <td>$row->{score} &nbsp; &nbsp; </td>\n");
	add(" <td><table><tr><td>$row->{comment}</td></tr></table></td>\n");
	add(" <td>");
	if ($row->{donorid} == $Donor->{donorid}) {
	    add("<a href=\"removecomment.cgi?$row->{commentid}\"><font size=\"-1\">Delete</font></a>");
	} else {
	    add("&nbsp;");
	}
	add("</td>\n");
	add("</tr>\n");
    }
    add("</table>\n");

    add(DOW_HTML_Footer($Donor));
}
