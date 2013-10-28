#!/usr/bin/perl -w
#
# Show shop contents.
#

use strict;
use Getopt::Std;

use dow;

use vars qw($opt_s);

my ($Donor, $Type, $Orderby);

$Donor = ProcessDowCommandline();

$opt_s = 'stRypum';
getopts('s:u:') or usage();

if ($#ARGV != 0) {
    usage();
}

$Type = $ARGV[0];
if ($Type !~ /^\s*[0-9]+\s*$/ || $Type < 1 || $Type > 15) {
    usage();
}

$Orderby = GenerateOrderBy($opt_s, ('s' => 'system',
				    'm' => 'item',
				    't' => 'tech',
				    'y' => 'yield',
				    'p' => 'price',
				    'r' => 'reliability',
				    'u' => 'turn'));

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: shoptype.cgi?Type<br> &nbsp; Type is a module type NUMBER.");
}

sub GeneratePage {
    my($typename, $sth, $row);
    my($yield, $reliability, $price, $sa, $tech);

    $typename = GetShopItemName($Type) . "s";
    add(DOW_HTML_Header($Donor, "DOW Shop Data - $typename"));
    add("<h1>DOW Shop Data - $typename</h1>");
    add("<p>Click on the column label to sort by that column. Click it again to reverse the sort order.\n<p><hr><p>\n");
    add("<table>\n");
    add("<tr>\n");

    $sa = GenerateSortArg($opt_s, 's');
    add("<th align=\"left\"><a href=\"shoptype.cgi?-s+$sa+$Type\">System</a>&nbsp;&nbsp;&nbsp;</th>");

    $sa = GenerateSortArg($opt_s, 'm');
    add("<th align=\"left\"><a href=\"shoptype.cgi?-s+$sa+$Type\">Module</a></th>");

    $sa = GenerateSortArg($opt_s, 't');
    add("<th align=\"left\"><a href=\"shoptype.cgi?-s+$sa+$Type\">Tech Level</a>&nbsp;&nbsp;&nbsp;</th>");

    $sa = GenerateSortArg($opt_s, 'y');
    add("<th align=\"left\"><a href=\"shoptype.cgi?-s+$sa+$Type\">Energy<br>Yield</a></th>");

    $sa = GenerateSortArg($opt_s, 'r');
    add("<th align=\"right\">&nbsp;&nbsp;<a href=\"shoptype.cgi?-s+$sa+$Type\">Rely</a></th>");

    $sa = GenerateSortArg($opt_s, 'p');
    add("<th align=\"right\">&nbsp;&nbsp;&nbsp;<a href=\"shoptype.cgi?-s+$sa+$Type\">Price</a></th>");

    $sa = GenerateSortArg($opt_s, 'u');
    add("<th align=\"left\">&nbsp;&nbsp;&nbsp;<a href=\"shoptype.cgi?-s+$sa+$Type\">Last Update</a></th>");

    add("</tr>\n");
    
#    $sth = mydo("select s1.* from shop s1 left join shop s2 on (s1.turn<s2.turn and s1.system=s2.system) where s2.turn is null and s1.type=? $Orderby;", $Type);
    $sth = mydo("select s1.* from shop s1, (select system, max(turn) as turn from shop group by system) s2 where s1.system = s2.system and s1.turn=s2.turn and s1.type=? $Orderby;", $Type);    


    while ($row = $sth->fetchrow_hashref()) {
	$yield = getelem($row, 'yield');
	$reliability = getelem($row, 'reliability');
	if ($Donor->{secreturl} =~ m|^http://tbg.fyndo.com/tbg/share_[A-Z][a-z]*.htm$|) {
	    $price = '';
	} else {
	    $price = getelem($row, 'price');
	}
	$tech = TechLevelToName($row->{tech});

	add("<tr>\n");
	add("<td><a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a>&nbsp;&nbsp;&nbsp;</td>");
	add("<td>$row->{item}&nbsp;&nbsp;&nbsp;</td>");
	add("<td>$tech&nbsp;&nbsp;&nbsp;</td>");
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
