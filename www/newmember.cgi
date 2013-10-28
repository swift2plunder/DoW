#!/usr/bin/perl -w
#
# Create a new member.
#

use strict;

use dow;

my $Donor = ProcessDowCommandline();

if ($#ARGV != -1) {
    usage();
}

if ($Donor->{donorid} != 1) {
    herror("Only the DOW Admin may do this.");
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: newmember.cgi");
}

sub GeneratePage {
    my($nid);
    $nid = SelectOne("select max(donorid) from donors;") + 1;
    add(DOW_HTML_Header($Donor, "DOW - Add New Member"));
    add("<h1>Add New Member</h1>");
    add("<form method=post action=\"newmembersubmit.cgi\">\n");
    add("<input name=dow_pw type=hidden value=\"$Donor->{dow_pw}\">\n");
    add("<table>\n");

    add("<tr>\n");
    add(" <td>Donorid</td>\n");
    add(" <td><input type=text size=10 name=donorid value=$nid></td>\n");
    add("</tr>\n\n");
    
    add("<tr>\n");
    add(" <td>Ship Name</td>\n");
    add(" <td><input type=text size=100 name=ship></td>\n");
    add("</tr>\n\n");

    add("<tr>\n");
    add(" <td>Label in DOW</td>\n");
    add(" <td><input type=text size=100 name=label></td>\n");
    add("</tr>\n\n");

    add("<tr>\n");
    add(" <td>Salutation</td>\n");
    add(" <td><input type=text size=100 name=salutation></td>\n");
    add("</tr>\n\n");


    add("<tr>\n");
    add(" <td>Email</td>\n");
    add(" <td><input type=text size=100 name=email></td>\n");
    add("</tr>\n\n");

    add("<tr>\n");
    add(" <td>Secret URL</td>\n");
    add(" <td><input type=text size=100 name=secreturl></td>\n");
    add("</tr>\n\n");

    add("</table>\n<input type=submit> &nbsp; <input type=reset>\n");
    add("</form>");
    add(DOW_HTML_Footer($Donor));
}
