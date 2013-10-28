#!/usr/bin/perl -w
#
# Show terminals.
#

use strict;
use Getopt::Std;

use dow;

use vars qw($opt_m $opt_s $opt_t $opt_y);

my($Donor, $Orderby, @Techs, @Types);

$opt_s = 'tmRYpsu';
$opt_t = '';
$opt_y = '';
$opt_m = 0;

if (exists($ENV{REMOTE_USER})) {
    $Donor = ProcessDowCommandline();
} elsif (exists($ENV{CONTENT_LENGTH})) {
    ReadFormData();
} else {
    herror("Couldn't get remote_user or form data!");
}

getopts('ms:t:y:') or usage();

if ($opt_t ne '') {
    @Techs = split(//, $opt_t);
}

if ($opt_y ne '') {
    @Types = map { hex($_); } split(//, $opt_y);
}

if ($#ARGV != -1) {
    usage();
}

$Orderby = GenerateOrderBy($opt_s, ('s' => 'system',
				    't' => 'tech',
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
    herror("Usage: searcshop.cgi?-m+-s+stmypru<br> &nbsp; -m  Use map view (otherwise, listview)");
}

sub GeneratePage {
    my(@typeselect, @techselect, $type, $tech, $str, $mapselected, $sth, $row);
    add(DOW_HTML_Header($Donor, "DOW - Search Shops"));

    if ($#Techs >= 0 || $#Types >= 0) {
	mydo("create temp table shoptmp () inherits (shop);");
	$sth = mydo("select system, max(turn) from shop group by system;");
	while ($row = $sth->fetchrow_hashref()) {
	    mydo("insert into shoptmp select * from shop where system=? and turn=? and tech in (" . join(", ", @Techs) . ") and type in (" . join(", ", @Types) . ");", $row->{system}, $row->{max});
	}
	$sth->finish();
	
	$sth = mydo("select * from shoptmp $Orderby;");

	if ($opt_m) {
	    MapView($sth);
	} else {
	    ListView($sth);
	}
	$sth->finish();
	mydo("drop table shoptmp;");
    }
    @typeselect = ('','','','','','','','','','','','','','','');
    @techselect = ('','','','','','');

    if ($#Techs >= 0 || $#Types >= 0) {
	foreach $type (@Types) {
	    $typeselect[$type-1] = ' selected';
	}	    
	foreach $tech (@Techs) {
	    $techselect[$tech-1] = ' selected';
	}	    
    } else {
	$typeselect[0] = ' selected';
	$techselect[0] = ' selected';
    }

    if ($opt_m) {
	$mapselected = ' checked';
    } else {
	$mapselected = '';
    }

    $str = <<"EndOfHTML";
<form method=post action=\"searchshop.cgi\">
<input name=dow_pw type=hidden value=\"$Donor->{dow_pw}\">

<select name=type size=6 multiple>
        <option value=1$typeselect[0]>Warp Drives</option>
	<option value=2$typeselect[1]>Impulse Drives</option>
	<option value=3$typeselect[2]>Sensors</option>
	<option value=4$typeselect[3]>Cloaks</option>
	<option value=5$typeselect[4]>Life Support</option>
	<option value=6$typeselect[5]>Sickbays</option>
	<option value=7$typeselect[6]>Shields</option>
	<option value=8$typeselect[7]>Rams</option>
	<option value=9$typeselect[8]>Guns</option>
	<option value=10$typeselect[9]>Disruptors</option>
	<option value=11$typeselect[10]>Lasers</option>
	<option value=12$typeselect[11]>Missiles</option>
	<option value=13$typeselect[12]>Drones</option>
	<option value=14$typeselect[13]>Fighters</option>
	<option value=15$typeselect[14]>Pods</option>
</select>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<select name=tech size=6 multiple>
     <option value=1$techselect[0]>Primitive</option>
     <option value=2$techselect[1]>Basic</option>
     <option value=3$techselect[2]>Mediocre</option>
     <option value=4$techselect[3]>Advanced</option>
     <option value=5$techselect[4]>Exotic</option>
     <option value=6$techselect[5]>Magic</option>
</select>
<p>
<input type=checkbox name=mapview value=true$mapselected> Map View
<p><input type=submit> &nbsp; <input type=reset>
</form>
EndOfHTML
    add($str);
    add(DOW_HTML_Footer($Donor));
}

sub MapView {
    my($sth) = @_;
    my($row, %system2tag);
    while ($row = $sth->fetchrow_hashref()) {
	$system2tag{$row->{system}} = "<img src=\"bigred.gif\">";
    }
    add(MakeMapGeneralNew($Donor->{ship}, \%system2tag, "<img src=\"smallgray.gif\">"));
    add("<hr>\n");
}

sub ListView {
    my($sth) = @_;
    my($row, $sa, $yield, $reliability, $price);

    add("<h1>Search Shops</h1>");

    add("<table>\n");
    add("<tr>\n");
    
    $sa = GenerateArg('s');
    add("<th align=\"left\"><a href=\"searchshop.cgi?-s+$sa\">System</a>&nbsp;&nbsp;&nbsp;</th>");
    
    $sa = GenerateArg('m');
    add("<th align=\"left\"><a href=\"searchshop.cgi?-s+$sa\">Module</a></th>");
    
    $sa = GenerateArg('t');
    add("<th align=\"left\"><a href=\"searchshop.cgi?-s+$sa\">Tech</a></th>\n");
    $sa = GenerateArg('y');
    add("<th align=\"center\"><a href=\"searchshop.cgi?-s+$sa\">Energy<br>Yield</a></th>");
    
    $sa = GenerateArg('r');
    add("<th align=\"right\">&nbsp;&nbsp;<a href=\"searchshop.cgi?-s+$sa\">Rely</a></th>");
    
    $sa = GenerateArg('p');
    add("<th align=\"right\">&nbsp;&nbsp;&nbsp;<a href=\"searchshop.cgi?-s+$sa\">Price</a></th>");
    
    $sa = GenerateArg('u');
    add("<th align=\"left\">&nbsp;&nbsp;&nbsp;<a href=\"searchshop.cgi?-s+$sa\">Last Update</a></th>");
    
    add("</tr>\n");

    while ($row = $sth->fetchrow_hashref()) {
	$yield = getelem($row, 'yield');
	$reliability = getelem($row, 'reliability');
	$price = getelem($row, 'price');
	
	add("<tr>\n");
	add("<td><a href=\"system.cgi?" . UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a>&nbsp;&nbsp;&nbsp;</td>");
	add("<td>$row->{item}&nbsp; &nbsp; &nbsp;</td>");
	add("<td>" . TechLevelToName($row->{tech}) . "</td>\n");
	add("<td align=\"center\">$yield</td>");
	add("<td align=\"right\">&nbsp;&nbsp;&nbsp;$reliability</td>");
	add("<td align=\"right\">&nbsp;&nbsp;&nbsp;$price</td>");
	add("<td align=\"left\">&nbsp;&nbsp;&nbsp;$row->{turn}</td>");
	add("</tr>\n");
    }
    add("</table>\n");
    add("<hr>\n");
}

sub ReadFormData {
    my($buffer, @namevals, $nameval, $name, $value);
    OpenDB();
    read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'}) 
	or herror("Couldn't read form data");

    # Split up into variable/value pairs

    @namevals = split(/&/, $buffer);

    # Handle quoting

    foreach $nameval (@namevals) {
	($name, $value) = split(/=/, $nameval);

	# Bit of magic from the web...
	$value =~ tr/+/ /;
	$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
	$value =~ s/<!--(.|\n)*-->//g;
	if ($name eq 'tech') {
	    push(@Techs, $value);
	} elsif ($name eq 'type') {
	    push(@Types, $value);
	} elsif ($name eq 'dow_pw') {
	    $Donor = SelectOneRowAsHash("select * from donors where dow_pw=?;",
					$value);
	} elsif ($name eq 'mapview') {
	    $opt_m = 1;
	} else {
	    herror("Unknown tag $name in form");
	}
    }
}

sub getelem {
    my($row, $elem) = @_;
    if (exists($row->{$elem}) && defined($row->{$elem})) {
	return $row->{$elem};
    } else {
	return "&nbsp;";
    }
}

sub GenerateArg {
    my($str) = @_;
    my($ret);
    $ret = GenerateSortArg($opt_s, $str);
    if ($#Techs >= 0) {
	$ret .= '+-t+' . join('', @Techs);
    }
    if ($#Types >= 0) {
	$ret .= '+-y+' . join('', map { sprintf("%x", $_); } @Types);
    }
    return $ret;
}
