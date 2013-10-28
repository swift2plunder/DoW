#!/usr/bin/perl -w
#
# Display custom set
#
# Because this can be called either directly or from a form, we can't use
# REMOTE_USER. Don't call ProcessDowCommandline().
#
# As a result, access to this page isn't logged!
#

use strict;
use Getopt::Std;
use LWP::Simple;	# For downloading orders

use dow;

use vars qw($opt_q $opt_m $opt_u);

my (%Form, %Prefs, %Settings, %SystemToScore, %SystemToJumpcost, %SystemToResval, %SystemToRes, %SystemToDesc);
my ($Turn, $MapFile, $Donor);

$MapFile = '/Path/to/system.html';

map { $Prefs{$_} = undef; } qw(ood sn usn hw hwup hwne hwh hwc factory cfactory eadv euadv sadv suadv madv muadv wadv wuadv erogue srogue mrogue wrogue jumpcost resources hiringhall prison ocean eacad sacad macad wacad eschool sschool mschool wschool epadv spadv mpadv wpadv);

map { $Settings{$_} = undef; } qw(turn dow_pw default mapview);

getopts('qmu:') or usage();

if ($#ARGV != -1) {
    usage();
}

OpenDB();

if (!defined($opt_q)) {
    ReadFormData();
} else {
    FetchFormData();
}

Validate();	# Validates form data, sets %Prefs and %Settings
GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: customsetsubmit.cgi?-q+-m<br> &nbsp; If -q is given, use presets<br> &nbsp; If -m is given, use map view.");
}

sub GeneratePage {
    my($sth, $row, @systems, @lowsys, @hisys, $system);

    $Turn = $Settings{turn};

    # Use turn as random seed (for out of date obfuscation)

    srand($Turn);

    
    # Handle setting default values
    if (exists($Settings{default}) && defined($Settings{default}) &&
	$Settings{default} eq 'true') {
	SetDefaults();
    }

    # Initialize scores and descs
    $sth = mydo("select distinct system from starcoords;");
    while ($row = $sth->fetchrow_hashref()) {
	$SystemToScore{$row->{system}} = 0;
	$SystemToResval{$row->{system}} = 0;
	$SystemToJumpcost{$row->{system}} = 0;
	$SystemToDesc{$row->{system}} = [];
	$SystemToRes{$row->{system}} = [];
    }
    $sth->finish();

    add(DOW_HTML_Header($Donor, "DOW Custom Set"));
    add("<h1>DOW Custom Set</h1>");
    
    DoJump();         # Does NOT call ScoreSystem()

    DoStarnet();
    DoHomeworld();
    DoFactory();
    DoAdventure();

    DoOutOfDate();

    DoRogue('Engineering', 'e');
    DoRogue('Science', 's');
    DoRogue('Medical', 'm');
    DoRogue('Weaponry', 'w');

    ScoreSystem($Prefs{hiringhall}, "Hiring Hall",
		"select distinct system from statics where item=?;",
		'Hiring Hall');

    ScoreSystem($Prefs{prison}, "Prison",
		"select distinct system from statics where item=?;",
		"Prison");

    ScoreSystem($Prefs{ocean}, "Ocean",
		"select distinct system from statics where item=?;",
		"Ocean");

    ScoreSystem($Prefs{eacad}, "Engineering Academy",
		"select distinct system from statics where item=?;",
		'Engineering Academy');

    ScoreSystem($Prefs{sacad}, "Science Academy",
		"select distinct system from statics where item=?;",
		'Science Academy');

    ScoreSystem($Prefs{macad}, "Medical Academy",
		"select distinct system from statics where item=?;",
		'Medical Academy');

    ScoreSystem($Prefs{wacad}, "Weaponnry Academy",
		"select distinct system from statics where item=?;",
		'Weaponry Academy');

    ScoreSystem($Prefs{eschool}, "Engineering School",
		"select distinct system from statics where item=?;",
		'Engineering School');

    ScoreSystem($Prefs{sschool}, "Science School",
		"select distinct system from statics where item=?;",
		'Science School');

    ScoreSystem($Prefs{mschool}, "Medical School",
		"select distinct system from statics where item=?;",
		'Medical School');

    ScoreSystem($Prefs{wschool}, "Weaponry School",
		"select distinct system from statics where item=?;",
		'Weaponry School');

    DoResource();     # Does NOT call ScoreSystem()

    if ($opt_m || 
	(exists($Settings{mapview}) && defined($Settings{mapview}) && 
	 $Settings{mapview} eq 'true')) {
	add("Go to <a href=\"customsetsubmit.cgi?-q\">List View</a>.<p><hr>");
	AddCustomMap();
    } else {
	add("Go to <a href=\"customsetsubmit.cgi?-q+-m\">Map View</a>.<p><hr>");
	add("<table border>");
	add("<tr><th>System</th><th>Score</th><th>Jump</th><th>Value of Resources</th><th>Explanation</th></tr>\n");
	@systems = sort { $SystemToScore{$b} <=> $SystemToScore{$a} } keys %SystemToScore;
	foreach $system (@systems) {
	    last if ($SystemToScore{$system} <= 0);
	    add("<tr>\n");
	    add(" <td><a href=\"system.cgi?" . UncanonicalizeSystem($system) .
		"\">$system</a></td>\n");
	    add(" <td>$SystemToScore{$system}</td>\n");
	    add(" <td>$SystemToJumpcost{$system}</td>\n");
	    if ($SystemToResval{$system} > 0) {
		add(" <td>$SystemToResval{$system} <font size=\"-1\">(");
		add(join(", ", @{$SystemToRes{$system}}));
		add(")</font></td>\n");
	    } else {
		add("<td>&nbsp;</td>\n");
	    }
	    add(" <td><font size=\"-1\">" . join(", ", @{$SystemToDesc{$system}}), "&nbsp;</font></td>\n");
	    add("</tr>\n");
	}
	add("</table>");
    }

    add(DOW_HTML_Footer($Donor));
}

sub DoResource {
    my($sth, $row, $ssth, $srow, $str);
    my(%res);        # Resource name => amount of resource
    my(@res);	     # set to keys(%res)
    my($res, $gotone);
    if ($Prefs{resources} == 0) {
	return;
    }

    # Medicine

    $sth = mydo("select * from medicine where ship=? and turn=?;", $Donor->{ship}, $Turn);
    $row = $sth->fetchrow_hashref();
    if (defined($row) && exists($row->{system}) && defined($row->{system})) {
	$SystemToScore{$row->{system}} += $Prefs{resources} * $row->{value};
	$SystemToResval{$row->{system}} += $row->{value};
	push(@{$SystemToRes{$row->{system}}}, "Medicine");
    }
    $sth->finish();

    # Other stuff

    $gotone = 0;
    $sth = mydo("select pods.resource, sum(n) from pods, factories where pods.resource=factories.resource and donorid=? and turn=? and n>0 group by pods.resource;", $Donor->{donorid}, $Turn);
    while ($row = $sth->fetchrow_hashref()) {
	$res{$row->{resource}} = $row->{sum};
    }
    $sth->finish();

    # Process orders to update number of resources carried.
    
    if ($Form{useorders}) {
	ProcessOrders(\%res);
    }

    @res = keys(%res);
    if ($#res < 0) {
	return;
    }
#    foreach $res (@res) {
#	print STDERR "$res = $res{$res}\n";
#    }

    $str = "select distinct system, max(turn) from trade where resource in ('" . join("', '", map { s/\'/\\\'/g; $_; } @res) . "') group by system ;";

#    print STDERR "$str\n";
    $ssth = mydo($str);

    # $ssth = mydo("select distinct system, max(turn) from trade where resource in ('" . join("', '", map { s/\'/\\'/g; $_; } @res) . "') group by system ;");
    
    while ($srow = $ssth->fetchrow_hashref()) {
	foreach $res (@res) {
	    $res =~ s/\\//g;
#	    print STDERR "res='$res' count='$res{$res}', sys='$srow->{system}', max='$srow->{max}'\n";
	    $sth = mydo("select * from trade where system=? and turn=? and resource=? limit $res{$res};", $srow->{system}, $srow->{max}, $res);
	    while ($row = $sth->fetchrow_hashref()) {
		$SystemToScore{$srow->{system}} += $Prefs{resources} * $row->{price};
		$SystemToResval{$srow->{system}} += $row->{price};
		push(@{$SystemToRes{$srow->{system}}}, $row->{resource});
	    }
	}
    }
}

sub DoStarnet {
    # All starnets
    ScoreSystem($Prefs{sn}, "StarNet", "select system from sysstarnet;");
    
    # Starnets you haven't accessed
    ScoreSystem($Prefs{usn}, "Unaccessed StarNet", "select system from sysstarnet where system not in (select system from terminals where turn=? and donorid=?);", $Turn, $Donor->{donorid});
}

sub DoHomeworld {
    # All homeworlds
    ScoreSystem($Prefs{hw}, "Homeworld", "select system from aliens;");

    # Homeworlds with uncured plagues
    ScoreSystem($Prefs{hwup}, "Uncured Plague", "select system from aliens where system not in (select system from plagues where turn=? and donorid=?);", $Turn, $Donor->{donorid});
    
    # Homeworlds of aliens who are not your enemy
    ScoreSystem($Prefs{hwne}, "Not an Enemy", "select system from aliens where race not in (select who from enemies where turn=? and donorid=?);", $Turn, $Donor->{donorid});

    # Homeworld of hostile alien
    ScoreSystem($Prefs{hwh}, "Hostile Homeworld",
		"select system from aliens where alignment='Hostile';");

    # Homeworld of chaotic alien
    ScoreSystem($Prefs{hwc}, "Chaotic Homeworld",
		"select system from aliens where alignment='Chaotic';");
}

sub DoFactory {
    # All Factories
    ScoreSystem($Prefs{factory}, "Factory", "select system from factories;");

    # Contraband Factories
    ScoreSystem($Prefs{cfactory}, "Contraband Factory", "select system from factories where resource like '%!%';");
}

# If trade data is older than 4 turns OR never visited
# by DOW OR visited by DOW more than 10 turns ago. Also remove 20% to try to
# obfuscate who's in DOW.

sub DoOutOfDate {
    my($sth, $vsth, $tsth, $row, $system, $vrow, $trow, $weight);
    $weight = $Prefs{ood};
    if ($weight == 0) {
	return;
    }
    $sth = mydo("select system from starcoords order by system;");
    $vsth = myprep("select max(turn) from shiploc, donors where system=? and shiploc.ship=donors.ship and turn<=?;");
    $tsth = myprep("select max(turn) from trade where system=? and turn<=?;");
    while ($row = $sth->fetchrow_hashref()) {

	# skip 20% of the time (trying to prevent tracking of DOW members).
	next if (rand() < 0.2);

	$system = $row->{system};

	myex($vsth, $system, $Turn);
	$vrow = $vsth->fetchrow_hashref();
	myex($tsth, $system, $Turn);
	$trow = $tsth->fetchrow_hashref();

	if (($system =~ /^Star \#([0-9]+)$/ && 
	     (!isset($vrow, 'max') || $vrow->{max} <= $Turn-10)) ||
	    (!isset($vrow, 'max') || $vrow->{max} <= $Turn-8 ||
	     (isset($trow, 'max') && $trow->{max} <= $Turn-3))) {
	    $SystemToScore{$system} += $weight;
	    push(@ {$SystemToDesc{$system}}, "Out of Date");
	}
    }

    $sth->finish();
    $tsth->finish();
    $vsth->finish();
}

sub DoRogue {
    my($label, $prefix) = @_;
    my($impulse, $lifesupport);

    $impulse = SelectOne("select lifesupportpercent from shipdata where donorid=? and turn=?;", 
			 $Donor->{donorid}, $Turn);
    $lifesupport = SelectOne("select impulsepercent from shipdata where donorid=? and turn=?;", 
			     $Donor->{donorid}, $Turn);
    
    ScoreSystem($Prefs{$prefix . 'rogue'}, "$label Rogues", 
		"select distinct system from rogues where field=? and turn=? and ((location='Impulse' and danger<=?) or (location='Life Support' and danger<=?));", 
		$label, $Turn, $impulse, $lifesupport);
}

sub DoAdventure {
    my($sth, $row, @reqs, $req, $qadv, $quadv);
    my($prefadvmin, $prefadvmax);

    # Get the latest ship levels
    $sth = mydo("select * from shipdata where donorid=? and turn=(select max(turn) from shipdata where donorid=?);", $Donor->{donorid}, $Donor->{donorid});
    $row = $sth->fetchrow_hashref();
    if (!defined($row)) {
	herror("Couldn't get ship data");
    }
    $sth->finish();

    $qadv = "select distinct system from adventures where turn=? and ((area='Engineering' and level<=$row->{engskill}) or (area='Science' and level<=$row->{sciskill}) or (area='Medical' and level<=$row->{medskill}) or (area='Weaponry' and level<=$row->{weapskill})) and (";

    @reqs = ();
    if ($Donor->{donorid} == 1) {
	@reqs = 'true';
    } else {
	foreach $req (qw(adv_all adv_newbie adv_done adv_high adv_hard)) {
	    if ($Donor->{$req}) {
		push(@reqs, "$req=true");
	    }
	}
	$sth->finish();
    }
    if ($#reqs == -1) {
	return;
    }

    $qadv .= join(' or ', @reqs) . ")";
    $quadv = "$qadv and name not in (select distinct name from skills where donorid=? and skills.area=adventures.area)";
    
    ScoreSystem($Prefs{eadv}, "Engineering Adventure", "$qadv and area='Engineering';", $Turn);
    ScoreSystem($Prefs{sadv}, "Science Adventure", "$qadv and area='Science';", $Turn);
    ScoreSystem($Prefs{madv}, "Medical Adventure", "$qadv and area='Medical';", $Turn);
    ScoreSystem($Prefs{wadv}, "Weaponry Adventure", "$qadv and area='Weaponry';", $Turn);

    ScoreSystem($Prefs{euadv}, "Uncompleted Engineering Adventure", "$quadv and area='Engineering';", $Turn, $Donor->{donorid});
    ScoreSystem($Prefs{suadv}, "Uncompleted Science Adventure", "$quadv and area='Science';", $Turn, $Donor->{donorid});
    ScoreSystem($Prefs{muadv}, "Uncompleted Medical Adventure", "$quadv and area='Medical';", $Turn, $Donor->{donorid});
    ScoreSystem($Prefs{wuadv}, "Uncompleted Weaponry Adventure", "$quadv and area='Weaponry';", $Turn, $Donor->{donorid});

    $prefadvmin = SelectOne("select prefadvmin from prefs where donorid=?",
			    $Donor->{donorid});
    $prefadvmax = SelectOne("select prefadvmax from prefs where donorid=?",
			    $Donor->{donorid});
    if (!defined($prefadvmin)) {
	$prefadvmin = 0;
    }
    if (!defined($prefadvmax)) {
	$prefadvmax = 32;
    }

    ScoreSystem($Prefs{epadv}, "Preferred Engineering Adventure", "$qadv and area='Engineering' and level>=$prefadvmin and level<=$prefadvmax;", $Turn);
    ScoreSystem($Prefs{spadv}, "Preferred Science Adventure", "$qadv and area='Science' and level>=$prefadvmin and level<=$prefadvmax;", $Turn);
    ScoreSystem($Prefs{mpadv}, "Preferred Medical Adventure", "$qadv and area='Medical' and level>=$prefadvmin and level<=$prefadvmax;", $Turn);
    ScoreSystem($Prefs{wpadv}, "Preferred Weaponry Adventure", "$qadv and area='Weaponry' and level>=$prefadvmin and level<=$prefadvmax;", $Turn);

} # DoAdventure

sub DoJump {
    my($system, $sth, $row, $cost);
    if ($Prefs{jumpcost} == 0) {
	return;
    }
    $system = SelectOne("select system from shiploc where ship=? and turn=?;", 
			$Donor->{ship}, $Turn);
    $sth = mydo("select system from starcoords;");
    while ($row = $sth->fetchrow_hashref()) {
	$cost = GetJumpCost($Donor->{donorid}, $Turn, $system, $row->{system});
	$SystemToScore{$row->{system}} += $Prefs{jumpcost} * $cost;
	$SystemToJumpcost{$row->{system}} += $cost;
    }
}

sub ScoreSystem {
    my($weight, $desc, $s, @args) = @_;
    if ($weight == 0) {
	return;
    }
    my(@systems, $system);
    @systems = SelectAll($s, @args);
    foreach $system (@systems) {
	$SystemToScore{$system} += $weight;
	push(@ {$SystemToDesc{$system}}, $desc);
    }
}

sub Validate {
    my($str);
    # Make sure each pref is set exactly once
    foreach $str (keys %Prefs) {
	if (defined($Prefs{$str})) {
	    herror("Got multiple prefs for '$str'");
	}
	if (!exists($Form{$str}) || !defined($Form{$str}) || 
	    $Form{$str} !~ /^\s*-?[0-9]+\s*$/) {
	    $Form{$str} = 0;
	}
	$Prefs{$str} = $Form{$str};
    }
    # Make sure each setting is set exactly zero or once
    foreach $str (keys %Settings) {
	if (defined($Settings{$str})) {
	    herror("Got multiple settings for '$str'");
	}
	if (!exists($Form{$str}) || !defined($Form{$str})) {
	    $Form{$str} = 0;
	}
	$Settings{$str} = $Form{$str};
    }
    # Now make sure there's nothing else in the %Form
    foreach $str (keys %Form) {
	if (!exists($Prefs{$str}) && !exists($Settings{$str}) && $str ne 'useorders') {
	    herror("Extra element in form '$str'");
	}
    }
    $Donor = SelectOneRowAsHash("select * from donors where dow_pw=?;", $Form{dow_pw});
}

# Get data from form
sub ReadFormData {
    my($buffer, @namevals, $nameval, $name, $value);

    # Make sure useorders is false if it isn't in the form
    $Form{useorders} = 0;
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
	
	$Form{$name} = $value;
    }
}

# Called with -q. Use presets from the user as given by env or -u arg.
sub FetchFormData {
    my($str, $ship, $donor);

    if (!exists($ENV{REMOTE_USER}) || !defined($ENV{REMOTE_USER})) {
	herror("Couldn't extract remote user.");
    }

    # For debugging.
    if (defined($opt_u) && SelectOne("select admin from donors where ship=?;", $ENV{REMOTE_USER})) {
	$ship = $opt_u;
	$ship =~ s/\\//g;
    } else {
	$ship = $ENV{REMOTE_USER};
    }
	
    $donor = SelectOneRowAsHash("select * from donors where ship=?;", $ship);
    $Form{turn} = SelectOne("select max(turn) from turnupdate where donorid=?;",
			    $donor->{donorid});
    $Form{mapview} = 0;
    $Form{default} = 0;
    $Form{dow_pw} = $donor->{dow_pw};
    
    if (!ExistsSelect("select donorid from customsetprefs where donorid=?;",
		      $donor->{donorid})) {
	mydo("insert into customsetprefs values (?);", $donor->{donorid});
    }

    foreach $str (keys %Prefs) {
	$Form{$str} = 
	    SelectOne("select $str from customsetprefs where donorid=?;",
		      $donor->{donorid});
    }
    $Form{useorders} = SelectOne("select useorders from customsetprefs where donorid=?;",
				 $donor->{donorid});
}

sub SetDefaults {
    my($str);
    if (!ExistsSelect("select donorid from customsetprefs where donorid=?;",
		      $Donor->{donorid})) {
	mydo("insert into customsetprefs values (?);", $Donor->{donorid});
    }

    foreach $str (keys %Prefs) {
	mydo("update customsetprefs set $str=? where donorid=?;", 
	     $Prefs{$str}, $Donor->{donorid});
    }
    if ($Form{useorders}) {
	mydo("update customsetprefs set useorders=true where donorid=?;", $Donor->{donorid});
    } else {
	mydo("update customsetprefs set useorders=false where donorid=?;", $Donor->{donorid});
    }
}


sub AddCustomMap {
    my($fh, $line, $image, $system1, $system2, %im, $mins, $maxs, $sys);
    my($shipsystem, $val);
    $shipsystem = SelectOne("select system from shiploc where ship=? and turn=?;",
			    $Donor->{ship}, $Turn);
    $mins = $SystemToScore{'Markab'};
    $maxs = $SystemToScore{'Markab'};
    foreach $sys (keys %SystemToScore) {
	if ($SystemToScore{$sys} < $mins) {
	    $mins = $SystemToScore{$sys};
	}
	if ($SystemToScore{$sys} > $maxs) {
	    $maxs = $SystemToScore{$sys};
	}
    }
#    add("<p>(Debug mins=$mins maxs=$maxs)<p>");
    if ($mins < 0) {
	$mins = 0;
    }
    foreach $sys (keys %SystemToScore) {
	if ($SystemToScore{$sys} < 0) {
	    $val = 15;
	} else {
	    $val = 15 - int(16 * ($SystemToScore{$sys}-$mins) / ($maxs-$mins+1));
	}
	$im{$sys} = sprintf("%%23ff%01xf%01xf", $val, $val);
    }
    
    $fh = new FileHandle($MapFile) or herror("Couldn't open mapfile $MapFile");
    while ($line = <$fh>) {
	chop($line);
	next if ($line eq "<html>");
	next if ($line eq "</html>");
	if ($line eq '</TR>' || $line eq '<TR ALIGN=CENTER>' || $line =~ m|^<TD COLSPAN=[0-9]+> </TD>$| || $line eq '<TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0>' || $line eq '</TABLE>') {
	    add("$line\n");
	} elsif ($line =~ m|<TD><IMG SRC=\"([^\"]+)\"></TD><TD COLSPAN=[0-9]+><a href=\"system.cgi\?([^\"]+)\">([^<]+)</a></TD><TD COLSPAN=[0-9]+> </TD>|) {
	    $image = $1;
	    $system1 = $2;
	    $system2 = $3;
	    $system1 = CanonicalizeSystem($system1);
	    $system2 = CanonicalizeSystem($system2);
	    if ($system1 ne $system2) {
		herror("System name mismatch! $system1 $system2");
	    }
	    $line =~ s/IMG SRC=\"$image\"/IMG SRC=\"planet.cgi?12+12+$im{$system1}\"/;
	    if (defined($shipsystem) && ($system1 eq CanonicalizeSystem($shipsystem))) {
		$line =~ s|<a href|<a style=\"color:\#ff0000;text-decoration:none\" href|;
	    } else {
		$line =~ s|<a href|<a style=\"color:\#000000;text-decoration:none\" href|;
	    }

	    add("$line\n");
	} else {
	    herror("Unexpected line in system '$line'");
	}
    }
    $fh->close();
}

sub ProcessOrders {
    my($res) = @_;
    my($orders, $line, $ordersurl, $turnfile, $inc, $fh, $n);
    my($option, $resource);
    $ordersurl = SelectOne("select secreturl from donors where donorid=?;", 
			   $Donor->{donorid});
    $ordersurl =~ s/\.htm$/.ord/;
    $orders = get($ordersurl);
    if (!defined($orders) || $orders =~ /^\s*$/) {
	return;	# No orders submitted. Just return.
    }
    $fh = new FileHandle("/Path/to/turns/$Turn/$Donor->{donorid}.html")
	or herror("Unable to access your turn. This should never happen.");
    $inc = 0;	# In <SELECT NAME="c"> tag
    while ($line = <$fh>) {
	if ($line =~ m|<SELECT NAME=\"c\"|) {
	    $inc = 1;
	} elsif ($inc) {
	    if ($line =~ m|</SELECT>|) {
		$inc=0;
		last;
	    } elsif ($line =~ m|<OPTION VALUE=(.*)>Sell ([0-9]+) (.*) to .* Colony for| ||
		     $line =~ m|<OPTION VALUE=(.*)>Buy ([0-9]+) (.*) for|) {
		$option = $1;
		$n = $2;
		$resource = $3;
		if ($line =~ m|<OPTION VALUE=$option>Sell|) {
		    $n = -$n;
		} elsif ($line !~ m|<OPTION VALUE=$option>Buy|) {
		    herror("No matching buy/sell order. This should never happen.");
		}
		if ($orders =~ /^c=$option$/m) {
		    #print STDERR "Transferring $n $resource\n";
		    $res->{$resource} += $n;
		}
	    }
	}
    }
    foreach $resource (keys(%$res)) {
	if ($res->{$resource} <= 0) {
	    delete($res->{$resource});
	}
    }
	
    $fh->close();
}

sub isset {
    my($row, $str) = @_;
    return exists($row->{$str}) && defined($row->{$str}) && $row->{$str} !~ /^\s*$/;
}
