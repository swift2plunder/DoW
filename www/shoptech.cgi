#!/usr/bin/perl -w
#
# Show shop contents.
#

use strict;
use Getopt::Std;

use dow;

use vars qw($opt_s);

my ($Donor, $TechLevel, $Orderby);

$Donor = ProcessDowCommandline();

$opt_s = 'smypru';
getopts('s:') or usage();

if ($#ARGV != 0) {
    usage();
}

$TechLevel = $ARGV[0];
if ($TechLevel !~ /^\s*[0-9]+\s*$/ || $TechLevel < 1 || $TechLevel > 6) {
    usage();
}

$Orderby = GenerateOrderBy($opt_s, ('s' => 'system',
				    'm' => 'type',
				    'y' => 'yield',
				    'p' => 'price',
				    'r' => 'reliability',
				    'u' => 'turn'));

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: shoptech.cgi?TechLevel<br> &nbsp; TechLevel is a NUMBER.");
}

sub GeneratePage {
    my($techname, $sth, $row);
    my($yield, $reliability, $price, $sa);

    $techname = TechLevelToName($TechLevel);
    add(DOW_HTML_Header($Donor, "DOW Shop Data - $techname Modules"));
    add("<h1>DOW Shop Data - $techname Modules</h1>");
    add("<p>Click on the column label to sort by that column. Click it again to reverse the sort order.\n<p><hr><p>\n");
    add("<table>\n");
    add("<tr>\n");

    $sa = GenerateSortArg($opt_s, 's');
    add("<th align=\"left\"><a href=\"shoptech.cgi?-s+$sa+$TechLevel\">System</a>&nbsp;&nbsp;&nbsp;</th>");

    $sa = GenerateSortArg($opt_s, 'm');
    add("<th align=\"left\"><a href=\"shoptech.cgi?-s+$sa+$TechLevel\">Module</a></th>");

    $sa = GenerateSortArg($opt_s, 'y');
    add("<th align=\"left\"><a href=\"shoptech.cgi?-s+$sa+$TechLevel\">Energy<br>Yield</a></th>");

    $sa = GenerateSortArg($opt_s, 'r');
    add("<th align=\"right\">&nbsp;&nbsp;<a href=\"shoptech.cgi?-s+$sa+$TechLevel\">Rely</a></th>");
    
    $sa = GenerateSortArg($opt_s, 'p');
    add("<th align=\"right\">&nbsp;&nbsp;&nbsp;<a href=\"shoptech.cgi?-s+$sa+$TechLevel\">Price</a></th>");
    
    $sa = GenerateSortArg($opt_s, 'u');
    add("<th align=\"left\">&nbsp;&nbsp;&nbsp;<a href=\"shoptech.cgi?-s+$sa+$TechLevel\">Last Update</a></th>");

    add("</tr>\n");

#    $sth = mydo("select s1.* from shop s1 left join shop s2 on (s1.turn<s2.turn and s1.system=s2.system) where s2.turn is null and s1.tech=? $Orderby;", $TechLevel);

    $sth = mydo("select s1.* from shop s1, (select system, max(turn) as turn from shop group by system) s2 where s1.system = s2.system and s1.turn=s2.turn and s1.tech=? $Orderby;", $TechLevel);    

    while ($row = $sth->fetchrow_hashref()) {
	$yield = getelem($row, 'yield');
	$reliability = getelem($row, 'reliability');
	if ($Donor->{secreturl} =~ m|^http://tbg.fyndo.com/tbg/share_[A-Z][a-z]*.htm$|) {
	    $price = '';
	} else {
	    $price = getelem($row, 'price');
	}

	add("<tr>\n");
	add("<td><a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a>&nbsp;&nbsp;&nbsp;</td>");
	add("<td>$row->{item}&nbsp; &nbsp; &nbsp;</td>");
	add("<td align=\"left\">$yield</td>");
	add("<td align=\"right\">&nbsp;&nbsp;&nbsp;$reliability</td>");
	add("<td align=\"right\">&nbsp;&nbsp;&nbsp;$price</td>");
	add("<td align=\"left\">&nbsp;&nbsp;&nbsp;$row->{turn}</td>");
	add("</tr>\n");
    }
    add("</table>\n");
    $sth->finish();
    add(DOW_HTML_Footer($Donor));
}

sub getelem {
    my($row, $elem) = @_;
    if (exists($row->{$elem}) && defined($row->{$elem})) {
	return $row->{$elem};
    } else {
	return "&nbsp;";
    }
}
