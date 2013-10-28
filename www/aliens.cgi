#!/usr/bin/perl -w
#
# Show aliens info
#

use strict;
use Getopt::Std;

use dow;

use vars qw($opt_s);

my($Donor, $Orderby);

$Donor = ProcessDowCommandline();

$opt_s = 'ELrahp';

getopts('s:') or usage();

if ($#ARGV != -1) {
    usage();
}

$Orderby = GenerateOrderBy($opt_s, ('r' => 'race',
				    'a' => 'alignment',
				    'h' => 'system',
				    'p' => 'area',
				    'e' => 'enemy', 
				    'l' => 'skilllevel'));

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: aliens.cgi?-s+ELrahp");
}

sub GeneratePage {
    my($sth, $row, $turn, $sa);

    $turn = SelectOne("select max(turn) from enemies where donorid=?;",
		      $Donor->{donorid});

    # Create a tmp table so sorting works

    mydo("create temp table alientmp (enemy boolean default false) inherits (aliens);");
    mydo("insert into alientmp (select * from aliens);");
    mydo("update alientmp set enemy=true where race in (select who from enemies where donorid=? and turn=?);",
	 $Donor->{donorid}, $turn);
    $sth = mydo("select * from alientmp $Orderby;");

    add(DOW_HTML_Header($Donor, "DOW Alien Race Information for $Donor->{ship}"));
    add("<h1>DOW Alien Race Information for $Donor->{ship}</h1>\n");
    add("<p>Click on the column header to sort by that column. Click on it again to sort in the reverse order.");
    add("<p>Go to <a href=\"alienmap.cgi\">Map View</a>.<hr>");
    add("<table>\n<tr>");

    $sa = GenerateSortArg($opt_s, 'r');
    add("<th align=left><a href=\"aliens.cgi?-s+$sa\">Race</a></th>");
    $sa = GenerateSortArg($opt_s, 'l');
    add("<th align=left><a href=\"aliens.cgi?-s+$sa\">Level</a></th>\n");
    $sa = GenerateSortArg($opt_s, 'a');
    add("<th align=left><a href=\"aliens.cgi?-s+$sa\">Align</a></th>");
    $sa = GenerateSortArg($opt_s, 'h');
    add("<th align=left><a href=\"aliens.cgi?-s+$sa\">Homeworld</a> &nbsp; &nbsp; </th>");
    $sa = GenerateSortArg($opt_s, 'p');
    add("<th align=left><a href=\"aliens.cgi?-s+$sa\">Politics</a></th>");
    $sa = GenerateSortArg($opt_s, 'e');
    add("<th><a href=\"aliens.cgi?-s+$sa\">Enemy?</a></th>");
    
    add("</tr>\n");
    
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr>\n");
	add("<td><a href=\"alien.cgi?$row->{race}\">$row->{race}</a> &nbsp; &nbsp; </td>\n");
	add("<td>$row->{skilllevel}&nbsp;&nbsp;</td>\n");
	add("<td>$row->{alignment} &nbsp; &nbsp; </td>\n");
	add("<td><a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a></td>\n");
   	add("<td>$row->{area} &nbsp; &nbsp; </td>\n");
	if ($row->{enemy}) {
	    add("<td>Yes</td>\n");
	} else {
	    add("<td>No</td>\n");
	}
    }
    $sth->finish();
    mydo("drop table alientmp;");
    add("</table>\n");
    add("<h3>Note</h3>Alien ships generate with modules of tech level equal to the level listed plus or minus 1 with a minimum of 1.<p>\n");
    add(DOW_HTML_Footer($Donor));
}
