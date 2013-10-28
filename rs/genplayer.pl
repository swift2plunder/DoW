#!/usr/bin/perl -w
#
# Generate player info from local cached turn
#

use dow;

$MaxLineLength = 60;
$TopDir = '/Path/to/rs';

if ($#ARGV != 0) {
    usage();
}

$DonorID = $ARGV[0];

OpenDB();

$Donor = SelectOneRowAsHash("select * from donors where donorid=?;", $DonorID);
#print "Generating shipdata.c for $Donor->{ship} ($DonorID)\n";

ReadPrefs();

$Turn = SelectOne("select max(turn) from turnupdate where donorid=?;", $DonorID);
$Path = "/Path/to/turns/$Turn/$DonorID.html";
$FH = new FileHandle($Path) or die "Could not open $Path: $!";
$OFH = new FileHandle(">$TopDir/shipdata.c") or die "Could not write to shipdata.c: $!";

$Verbose = 0;

$EngSkill = "UNKNOWN";
$TotalMass = "UNKNOWN";
$InitialLoc = "UNKNOWN";
$WarpTech = 0;
$InArtifacts = 0;
$Who = "UNKNOWN";
$InModules = 0;
$TotalEnergy = "UNKNOWN";

%WarpTechs = ("Primitive" => 1,
	      "Basic" => 2,
	      "Mediocre" => 3,
	      "Advanced" => 4,
	      "Exotic" => 5,
	      "Magic" => 6);

foreach my $res ("Emperors' New Clothes", "Euphoria (!)", "Tea",
	      "Eye Robots", "Hankies", "Ninja Beer", "Jumpers",
	      "Steely Knives (!)", "Winegums", "Puddings", "Beards",
	      "Web Pages", "Fudge", "Xylophones", "Snowmen",
	      "Windows (!)", "Sharp Sticks (!)", "Scrap", "Surprises",
	      "New Tricks", "Chocolate", "Marzipan", "Lists",
	      "Dilithium", "Boardgames", "Mittens", "Videos",
	      "Ray-guns (!)", "Hats", "Elvis Memorabilia", "Old Songs",
		 "Quad Trees", "Empty") {
    $Resources{$res} = 1;
}

while (<$FH>) {
    if (/To Boldly Go - Starship (.*), Turn/) {
	if ($Who ne "UNKNOWN") {
	    die "Got more than one title line";
	}
	$Who = $1;
	print STDERR "Setting Who to $Who\n" if $Verbose;
    } elsif (/<TR><TH>Engineering skills \(([0-9]+)/) {
	if ($EngSkill ne "UNKNOWN") {
	    die "Got more than one Engineering line";
	}
	$EngSkill = $1;
	print STDERR "Setting EngSkill to $EngSkill\n" if $Verbose;
    } elsif (/^<TR><TH COLSPAN=4 ALIGN=CENTER>.*$Who/) {
	$InModules = 1;
	print STDERR "Setting InModules to 1\n" if $Verbose;
    } elsif (/^<TR><TH COLSPAN=4 ALIGN=CENTER>/) {
	$InModules = 0;
	print STDERR "Setting InModules to 0\n" if $Verbose;
    } elsif ($InModules && /Mass = ([0-9]+), Energy Yield = /) {
	if ($TotalMass ne "UNKNOWN") {
	    die "Got more than one mass line";
	}
	$TotalMass = $1;
	print STDERR "Setting TotalMass to $TotalMass\n" if $Verbose;
    } elsif ($InModules && /^<TR ALIGN=CENTER><TD>(pod-[0-9]+D?)\s*<\/TD><TD>([0-9])<\/TD><TD>(.*)<\/TD><TD>([0-9])<\/TD><\/TR>$/) {
	$podid = $1;
	$capacity = $2;
	$cargo = $3;
	$holding = $4;
	
	$CurrentCargo += $holding;

#	print STDERR "Testing '$podid' against '$ExcludePods'\n" if $Verbose;

	if (index($ExcludePods, $podid) != -1) {
	    print STDERR "Excluding pod $podid\n" if $Verbose;
	} else {
	    if (exists($Resources{$cargo})) {
		if ($holding == 0) {
		    $cargo = "";
		}
		push(@PodCapacities, $capacity);
		push(@InitialLoad, $holding);
		push(@InitialLoad, "\"$cargo\"");
	    } else {
		print STDERR "\n\n   Unexpected cargo $cargo. Ignoring.\n\n";
	    }
	}
    } elsif ($InModules && /^<TR ALIGN=CENTER><TD>warp drive-[0-9]+D?\s*<\/TD><TD>(.*)<\/TD><TD>[0-9]+%<\/TD><TD>[0-9]+<\/TD><\/TR>$/) {
	$wt = $1;
	if (!exists($WarpTechs{$wt})) {
	    die "No such warp $wt";
	} else {
	    $WarpTech += $WarpTechs{$wt};
	}
    } elsif ($InitialLoc eq "UNKNOWN" && /\(ending turn at star system (.*) with \$([0-9]+) of energy/) {
	$InitialLoc = $1;
	$TotalEnergy = $2;
	$InitialLoc =~ s/S\#/Star \#/i;
	$InitialLoc =~ s/S([0-9]+)/S\#$1/i;
    } elsif ($InModules && /^<TR><TH>Artifact<\/TH>/) {
	$InArtifacts = 1;
	print STDERR "Setting InArtifacts to $InArtifacts\n" if $Verbose;
    } elsif ($InModules && $InArtifacts) {
	if (/^<TR ALIGN=CENTER><TD>.*<\/TD><TD>.*<\/TD><TD>.*<\/TD><TD>([0-9]+)<\/TD>/) {
	    print STDERR "Handling artifact line $_\n" if $Verbose;
	    foreach my $key (split('', $1)) {
		$Keys{$key} = 1;
	    }
	} elsif (! /^<\/TR>/) {
	    $InArtifacts = 0;
	}
    }
}

print STDERR "TotalMass = $TotalMass, CurrentCargo = $CurrentCargo\n" if $Verbose;
$EmptyMass = $TotalMass - $CurrentCargo;

# Compute energy as the total energy of your ship times your energypercent
# from the route simulator settings.
$InitialEnergy = int($TotalEnergy*SelectOne("select energypercent from rss where donorid=?;", $DonorID));

print $OFH "#define EMPTY_MASS	($EmptyMass)\n";
print $OFH "#define WARP_TECH	($WarpTech)\n";
print $OFH "#define ENG_SKILL	($EngSkill)\n";
print $OFH "#define INITIAL_ENERGY	($InitialEnergy)\n";
print $OFH "#define INITIAL_LOC	(\"$InitialLoc\")\n\n";

print $OFH "#define NPODS		(", ($#PodCapacities + 1), ")\n\n";

print $OFH "#define POD_CAPACITY	", join(', ', @PodCapacities), "\n";
print $OFH "#define INITIAL_LOAD	", join(', ', @InitialLoad), "\n\n";

@Keys = sort keys(%Keys);
if ($#Keys >= 0) {
    print $OFH "#define HASKEY(x) (x == ", join(' || x == ', @Keys), ")\n";
} else {
    print $OFH "#define HASKEY(x) (0)\n";
}

print $OFH "\n";


if (ExistsSelect("select * from rss where donorid=?;", $DonorID)) {
    print $OFH "#define MAX_JUMP_COST (" . SelectOne("select maxjump from rss where donorid=?;", $DonorID) . ")\n";

    print $OFH "#define MAX_PURCHASE (" . SelectOne("select maxpurchase from rss where donorid=?;", $DonorID) . ")\n";

    if (SelectOne("select olympian from rss where donorid=?;", $DonorID)) {
	print $OFH "#define OLYMPIAN (1)\n";
    } else {
	print $OFH "#define OLYMPIAN (0)\n";
    }

    if (SelectOne("select contraband from rss where donorid=?;", $DonorID)) {
	print $OFH "#define CONTRABAND (1)\n";
    } else {
	print $OFH "#define CONTRABAND (0)\n";
    }

    print $OFH "#define DEFAULT_NTURNS (", SelectOne("select nturns from rss where donorid=?;", $DonorID), ")\n";

    print $OFH "#define DEFAULT_CARGO_WEIGHT \"", SelectOne("select cargoweight from rss where donorid=?;", $DonorID), "\"\n";
    
} else {
    print $OFH "#define MAX_JUMP_COST (-1)\n";
    print $OFH "#define MAX_PURCHASE (-1)\n";
    print $OFH "#define OLYMPIAN (0)\n";
    print $OFH "#define CONTRABAND (0)\n";
    print $OFH "#define DEFAULT_NTURNS (5)\n";
    print $OFH "#define DEFAULT_CARGO_WEIGHT \"1.5\"\n";
}

GenerateSystemScores();
OutputSystemScores();

$FH->close();
$OFH->close();

CloseDB();

sub GenerateSystemScores {
    my($sth, $row, $sys);

    # Initialize scores and descs
    $sth = mydo("select distinct system from starcoords;");
    while ($row = $sth->fetchrow_hashref()) {
	$SystemToScore{$row->{system}} = 0;
    }
    $sth->finish();

    # Add in any bonuses specified by system_bonuses
    DoSystemBonuses();

    DoStarnet();
    DoHomeworld();
    DoFactory();
    DoAdventure();
    DoMedicine();

    # Out of date.
    # If trade data is older than 4 turns OR never visited by DOW OR visited by DOW more than 10 turns ago.

    ScoreSystem($Prefs{ood}, "Out of Date", 
		"(select distinct system from trade group by system having max(turn)<=?) UNION (select system from starcoords where system not in (select distinct system from shiploc, donors where shiploc.ship=donors.ship)) UNION ( select distinct system from shiploc, donors where shiploc.ship=donors.ship group by system having max(turn)<=?);",
		$Turn-4, $Turn-10);

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
} # GenerateSystems

sub DoMedicine {
    my($sth, $row);

    $sth = mydo("select * from medicine where ship=? and turn=?;", $Donor->{ship}, $Turn);
    $row = $sth->fetchrow_hashref();
    if (defined($row) && exists($row->{system}) && defined($row->{system})) {
	$SystemToScore{$row->{system}} += $row->{value};
    }
    $sth->finish();
}


sub DoSystemBonuses {
    my($sth, $row, $sysbonus, $sys, $bonus);

    $sth = mydo("select system_bonuses from rss where donorid=?", $DonorID);
    $row = $sth->fetchrow_hashref();
    if (!defined($row) || !exists($row->{system_bonuses}) ||
	!defined($row->{system_bonuses}) || $row->{system_bonuses} =~ /^\s*$/) {
	$sth->finish();
	return;
    }
    foreach $sysbonus (split(/\s*,\s*/, $row->{system_bonuses})) {
	if ($sysbonus =~ /^\s*(.*)\s+(-?[0-9]+)$/) {
	    $sys = $1;
	    $bonus = $2;
	    if (exists($SystemToScore{$sys})) {
		$SystemToScore{$sys} += $bonus;
		#print STDERR "Bonus to $sys of $bonus\n";
	    }
	}
    }
}


sub DoStarnet {
    # All starnets
    ScoreSystem($Prefs{sn}, "StarNet", "select system from sysstarnet;");
    
    # Starnets you haven't accessed
    ScoreSystem($Prefs{usn}, "Unaccessed StarNet", "select system from sysstarnet where system not in (select system from terminals where turn=? and donorid=?);", $Turn, $DonorID);
}

sub DoHomeworld {
    # All homeworlds
    ScoreSystem($Prefs{hw}, "Homeworld", "select system from aliens;");

    # Homeworlds with uncured plagues
    ScoreSystem($Prefs{hwup}, "Uncured Plague", "select system from aliens where system not in (select system from plagues where turn=? and donorid=?);", $Turn, $DonorID);
    
    # Homeworlds of aliens who are not your enemy
    ScoreSystem($Prefs{hwne}, "Not an Enemy", "select system from aliens where race not in (select who from enemies where turn=? and donorid=?);", $Turn, $DonorID);

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

sub DoRogue {
    my($label, $prefix) = @_;
    my($impulse, $lifesupport);

    $impulse = SelectOne("select lifesupportpercent from shipdata where donorid=? and turn=?;", 
			 $DonorID, $Turn);
    $lifesupport = SelectOne("select impulsepercent from shipdata where donorid=? and turn=?;", 
			     $DonorID, $Turn);
    
    ScoreSystem($Prefs{$prefix . 'rogue'}, "$label Rogues", 
		"select distinct system from rogues where field=? and turn=? and ((location='Impulse' and danger<=?) or (location='Life Support' and danger<=?));", 
		$label, $Turn, $impulse, $lifesupport);
}

sub DoAdventure {
    my($sth, $row, @reqs, $req, $qadv, $quadv);

    # Get the latest ship levels
    $sth = mydo("select * from shipdata where donorid=? and turn=(select max(turn) from shipdata where donorid=?);", $DonorID, $DonorID);
    $row = $sth->fetchrow_hashref();
    if (!defined($row)) {
	error("Couldn't get ship data");
    }
    $sth->finish();

    $qadv = "select distinct system from adventures where turn=? and ((area='Engineering' and level<=$row->{engskill}) or (area='Science' and level<=$row->{sciskill}) or (area='Medical' and level<=$row->{medskill}) or (area='Weaponry' and level<=$row->{weapskill})) and (";

    @reqs = ();
    if ($DonorID == 1) {
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

    ScoreSystem($Prefs{euadv}, "Uncompleted Engineering Adventure", "$quadv and area='Engineering';", $Turn, $DonorID);
    ScoreSystem($Prefs{suadv}, "Uncompleted Science Adventure", "$quadv and area='Science';", $Turn, $DonorID);
    ScoreSystem($Prefs{muadv}, "Uncompleted Medical Adventure", "$quadv and area='Medical';", $Turn, $DonorID);
    ScoreSystem($Prefs{wuadv}, "Uncompleted Weaponry Adventure", "$quadv and area='Weaponry';", $Turn, $DonorID);

} # DoAdventure

sub ScoreSystem {
    my($weight, $desc, $s, @args) = @_;
    if ($weight == 0) {
	return;
    }
    my(@systems, $system);
    @systems = SelectAll($s, @args);
    foreach $system (@systems) {
	$SystemToScore{$system} += $weight;
    }
}

sub OutputSystemScores {
    print $OFH "\nint SystemScore[NSTARS] = {\n";
    print $OFH &CommaWrap(map { $SystemToScore{$_}; }
	(
	 "Star #30", "Mizar", "Alcor", "Zosca", "Star #3", "Star #58", "Star #25",
	 "Star #22", "Star #60", "Kapetyn", "Star #33", "Star #36", "Star #41",
	 "Lupi", "Hydrae", "Adhara", "Star #20", "Cygni", "Star #42",
	 "Alphard", "Star #52", "Deneb", "Star #11", "Regulus", "Star #19",
	 "Mirfak", "Kochab", "Star #13", "Star #12", "Canis", "Star #9",
	 "Markab", "Star #21", "Algol", "Star #43", "Altair", "Star #35",
	 "Alioth", "Draconis", "Capella", "Star #17", "Star #49",
	 "Bootis", "Star #32", "Star #7", "Arcturus", "Fomalhaut",
	 "Tauri", "Star #40", "Wolf", "Rigel", "Canopus", "Star #10",
	 "Aldebaran", "Sirius", "Star #55", "Star #63", "Caph", "Star #51",
	 "Star #46", "Star #38", "Star #14", "Ceti", "Diphda", "Star #28",
	 "Thuban", "Pherda", "Olympus", "Star #26", "Star #27", "Kruger",
	 "Star #1", "Star #44", "Star #47", "Star #2", "Star #39", "Star #29", "Star #56",
	 "Star #45", "Spica", "Hamal", "Wezen", "Star #37", "Polaris",
	 "Barnard", "Star #8", "Rastaban", "Indi", "Star #6", "Lalande",
	 "Cephei", "Merak", "Star #54", "Castor", "Star #5", "Antares",
	 "Star #31", "Star #23", "Scorpii", "Star #16", "Lyrae", "Schedar",
	 "Star #61", "Aurigae", "Sadir", "Alnitak", "Star #62",
	 "Ophiuchi", "Centauri", "Star #15", "Crucis", "Procyon",
	 "Star #59", "Star #18", "Achernar", "Star #4", "Star #57", "Star #50", "Star #0",
	 "Star #53", "Star #34", "Vega", "Betelgeuse", "Star #48", "Star #24",
	 "Ross", "Mira", "Pollux", "Eridani"));
    print $OFH "\n};\n";
}

sub CommaWrap {
    my(@elems) = @_;
    my($str, $elem, $linelen, $el);
    $str = "  " . shift(@elems);
    $linelen = length($str);
    while ($#elems >= 0) {
	$elem = shift(@elems);
	$el = length($elem);
	if ($linelen+$el+2 > $MaxLineLength) {
	    $str .= ",\n  $elem";
	    $linelen = 2 + $el;
	} else {
	    $str .= ", $elem";
	    $linelen += 2 + $el;
	}
    }
    return $str;
}
    
sub error {
    print STDERR @_;
    exit;
}

sub ReadPrefs {
    my(@allprefs, $pref);

    @allprefs = qw(ood sn usn hw hwup hwne hwh hwc factory cfactory eadv euadv sadv suadv madv muadv wadv wuadv erogue srogue mrogue wrogue hiringhall prison ocean eacad sacad macad wacad eschool sschool mschool wschool);
    
    if (!ExistsSelect("select donorid from rss where donorid=?;", $DonorID)) {
	map { $Prefs{$_} = 0; } @allprefs;
	$ExcludePods = "";
    } else {
	foreach $pref (@allprefs) {
	    $Prefs{$pref} = SelectOne("select $pref from rss where donorid=?;", 
				      $DonorID);
	    if (!defined($Prefs{$pref}) || $Prefs{$pref} !~ /^[0-9]+$/) {
		$Prefs{$pref} = 0;
	    }
	}
	$ExcludePods = SelectOne("select excludepods from rss where donorid=?;",
				 $DonorID);	
    }    
}

sub usage {
    print STDERR "Usage: genplayer.pl player\n";
    exit(-1);
}
