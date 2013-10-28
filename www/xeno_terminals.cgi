#!/usr/bin/perl -w
#
# Show which terminals Xemo members have accessed
#

use strict;

use dow;

my($Donor);

$Donor = ProcessDowCommandline();

if (!$Donor->{xenoadmin}) {
    herror("This page is only available to Department of Xenology Adminstrators");
}

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: xeno_terminals.cgi");
}

sub GeneratePage {
    my($turn, @allxenos, @allterminals, %xeno2terms, %xeno2nterms, @terminals, $xeno);
    my(%sys2ship, %sys2nships, $system, @ships);
    add(DOW_HTML_Header($Donor, "Department of Xenology - Terminals Accessed"));
    add("<h1>Department of Xenology - Terminals Accessed</h1>\n");
    add("<table border>\n");
    add("<tr valign=top>\n");
    add("<th align=left>Member</th><th align=right>#&nbsp;&nbsp;&nbsp;</th><th align=left>Systems</th>\n");
    add("</tr>\n");

    $turn = SelectOne("select max(turn) from turnupdate;");    

    @allxenos = SelectAll("select ship from donors where xeno=true and label not like 'Anonymous%';");
    @allterminals = SelectAll("select system from sysstarnet;");

    foreach $xeno (@allxenos) {
	@terminals = SelectAll("select system from terminals, donors where terminals.donorid = donors.donorid and turn=? and donors.ship=? order by system;", $turn, $xeno);
	$xeno2terms{$xeno} = join(", ", map { "<a href=\"system.cgi?" . UncanonicalizeSystem($_) . "\">$_</a>" } @terminals);
	$xeno2nterms{$xeno} = $#terminals + 1;
    }

    foreach $xeno (sort { $xeno2nterms{$b} <=> $xeno2nterms{$a} } @allxenos) {
	add("<tr valign=top>\n");
	add(" <td><a href=\"shipsummary.cgi?$xeno\">$xeno</a>&nbsp;&nbsp;</td>\n");
	add(" <td align=right>$xeno2nterms{$xeno}&nbsp;&nbsp;&nbsp;</td>\n");
	add(" <td>$xeno2terms{$xeno}</td>\n");
	add("</tr>\n\n");
    }
    add("</table>\n");

    add("<p><hr><p><table border><tr><th align=left>System</th><th align=right>#&nbsp;&nbsp;&nbsp;</th><th align=left>Ships</th></tr>\n");
    foreach $system (@allterminals) {
	@ships = SelectAll("select ship from terminals, donors where terminals.donorid=donors.donorid and turn=? and terminals.system=? and donors.xeno=true and label not like 'Anonymous%';", $turn, $system);
	$sys2nships{$system} = $#ships + 1;
	$sys2ship{$system} = join(", ", map { "<a href=\"shipsummary.cgi?$_\">$_</a>" } @ships);
    }

    foreach $system (sort { $sys2nships{$a} <=> $sys2nships{$b} } @allterminals) {
	add("<tr valign=top>\n");
	add(" <td><a href=\"system.cgi?" . UncanonicalizeSystem($system) . "\">$system</a>&nbsp;&nbsp;</td>\n");
	add(" <td align=right>$sys2nships{$system}&nbsp;&nbsp;&nbsp;</td>\n");
	add(" <td>$sys2ship{$system}</td>\n");
    }
    add("</table>");
    add(DOW_HTML_Footer($Donor));
}
