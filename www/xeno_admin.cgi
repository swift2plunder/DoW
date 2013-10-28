#!/usr/bin/perl -w
#
# Institute of Xenology, administration
#

use strict;

use dow;

my $Donor = ProcessDowCommandline();

if ($#ARGV != -1) {
    usage();
}

if (!$Donor->{xenoadmin}) {
    herror("Only the admin may use this page");
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: xeno_admin.cgi");
}

sub GeneratePage {
    my($sth, $row, $turn);
    $turn = SelectOne("select max(turn) from turnupdate;");
    add(DOW_HTML_Header($Donor, "DOW - Institute of Xenology Administration"));
    add("<h1>DOW - Institute of Xenology Administration</h1>\n");
    add("<hr><p>\n");
    add("<form method=post action=\"xeno_add_entry.cgi\">\n");
    add("<input type=hidden name=dow_pw value=\"$Donor->{dow_pw}\">\n");
    add("<table>\n");
    add("<tr>");
    add(" <td align=right>Turn:</td>\n");
    add(" <td><input type=text name=turn size=5 value=$turn> &nbsp; &nbsp; \n");
    if ($Donor->{xenoadmin}) {
	add("Ship: <input name=ship type=text size=63></td>");
    } else {
	add("Ship: $Donor->{ship}</td>");
	add("<input type=hidden name=ship value=\"$Donor->{ship}\">");
    }
    add("</tr>\n");
    add("<tr>\n");
    add(" <td>Action:</td>");
    add(" <td><input name=action type=text size=80></td>\n");
    add("</tr></table><p>\n");    
    add("<input type=submit> &nbsp; <input type=reset>\n");
    add("</form>\n");
    add("<p><hr><p>\n");
    add("<table>\n");
    add("<tr><th align=left>Ship</th><th align=left>Turn</th><th align=left>Action</th><th>&nbsp;</th></tr>\n");
    $sth = mydo("select * from xeno_history order by turn desc;");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr><td><a href=\"shipsummary.cgi?$row->{ship}\">$row->{ship}</a> &nbsp; &nbsp; </td><td>$row->{turn} &nbsp; &nbsp; </td><td>$row->{action} &nbsp; &nbsp; </td>");
	if ($Donor->{xenoadmin}) {
	    add("<td><font size=\"-1\"><a href=\"xeno_delete.cgi?$row->{id}\">Delete</a></font></td>");
	} else {
	    add("<td>&nbsp</td>");
	}
	add("</tr>\n");		
    }
    add("</table>\n");
    add(DOW_HTML_Footer($Donor));
}

