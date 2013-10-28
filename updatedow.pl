#!/usr/bin/perl -w
######################################################################
#
# This is the script that reads turns and ships from the server
# and updates the database. It's grown a lot over time, so
# it's the messiest of the DOW scripts.
#
# In order to protect anonymity of DOW members, I've removed all the
# obfuscation code.
#
#
# This script is called by cron on Monday, Wednesday, and Friday at
# 2pm to update the database from the server. Note that if it fails,
# you must MANUALLY clean up the database (e.g. cleardow.pl) and
# MANUALLY call updatedow.pl yourself. The script calls postturn.sh
# once the database has updated.
#


use strict;
use DBI;
use FileHandle;
use Getopt::Std;
use LWP::Simple;
use LWP::UserAgent;
use IO::Scalar;

use dow;

use vars qw($opt_h $opt_t $opt_p);

#my $CacheOnly = 1;
my $CacheOnly = 0;

# Global variables
my $Top = '/Path/to/tbg';
my %SystemBuys;		# Used to track who buys what
my $Turn;		# Which turn we're trying to load
my %TechLevels;		# e.g. primitive => 1
my $TechRE;		# Legal techs (all lowercase, so use /i)
my $MessageFH = new FileHandle(">$Top/updatedow.messages");
$MessageFH->autoflush(1);
my $WarningFH = new FileHandle(">$Top/updatedow.warnings");
$WarningFH->autoflush(1);

my @UngetLines;		# Used with getline/ungetline

$opt_h = 0;
$opt_t = undef;

getopts('ht:p:') or usage();
usage() if $opt_h;

OpenDB();

if (defined($opt_t) && $opt_t != 0) {
    $Turn = $opt_t;
} else {
    $Turn = SelectOne("select max(turn) from turnupdate;");
    if (!defined($opt_p)) {
	$Turn++;
    }
}

LoadStaticData();

PreTurn();

UpdateTurns();

UpdateActive();

DoChecks();

UpdateAllShips();

PostTurn();

CloseDB();

message("Done.");
$MessageFH->close();
$WarningFH->close();

# For all ships accessible at or prior to this turn, create an entry.
# This is basically just a caching mechanism to speed up access.
sub UpdateAllShips {
    my($sth, $row);
    message("Setting allships\n");
    $sth = mydo("(select distinct ship from shiploc) UNION (select distinct ship from shipconfig) UNION (select distinct ship from influence) order by ship;");
    while ($row = $sth->fetchrow_hashref()) {
	next if ($row->{ship} eq "Unknown" ||
		 $row->{ship} eq "Neutral");
	next if (ExistsSelect("select * from allships where turn=? and ship=?;", 
			      $Turn, $row->{ship}));
	if (defined(RaceOfShip($row->{ship}))) {
	    mydo("insert into allships values(?, ?, ?);", $Turn, $row->{ship}, "Alien");
	} elsif (ExistsSelect("select * from activeships where turn=? and ship=?;", 
			      $Turn, $row->{ship})) {
	    mydo("insert into allships values(?, ?, ?);", $Turn, $row->{ship}, "Player");
	} else {
	    mydo("insert into allships values(?, ?, ?);", $Turn, $row->{ship}, "Retired");
	}
    }
    $sth->finish();
}

sub PreTurn {
    my($sth, $row, $lab);
    system("cp $Top/www/dow/updating.html $Top/www/dow/nodow.html");
    mydo("delete from probes;");

    # Update new settings.

    $sth = mydo("select * from newsettings;");
    while ($row = $sth->fetchrow_hashref()) {
	foreach $lab (qw(email secreturl dow_pw adv_newbie adv_done adv_high adv_hard adv_all shiploc shipconfig influence pub_adv_newbie pub_shop_newbie pub_trade obfuscate purgers dow_pw anonymous)) {
	    mydo("update donors set $lab=? where donorid=?;",
		 $row->{$lab}, $row->{donorid});
	}
    }
    $sth->finish();
    mydo("delete from newsettings;");
    # Rebuild passwords
    system("/Path/to/tbg/makedowpw.pl");
}

sub PostTurn {
    unlink("$Top/www/dow/nodow.html");

    # Run post turn stuff that doesn't add data to DOW
    # (e.g. static pages for non-DOW members, dow2, trade sim, etc.
    message(`/Path/to/tbg/postturn.sh`);
}

sub DoChecks {
    FixupInfluence();
}

sub GetTurn {
    my($donor) = @_;
    my($donorid, $fname, $content, $fh);
    $donorid = $donor->{donorid};
    $fname = "$Top/turns/$Turn/$donorid.html";

    if (!-e "$Top/turns/$Turn") {
	message("Making turn cache directory $Top/turns/$Turn");
	mkdir("$Top/turns/$Turn");
    }
    
    if (! -r $fname) {
	if ($CacheOnly) {
	    warning("Currently, only using cache ship turns"); #!!!
	    return undef;
	}
	message("Downloading $donor->{ship} from $donor->{secreturl}");
	$content = myget($donor->{secreturl});
	if (!defined($content)) {
	    warning("Unable to get $donor->{secreturl} for $donor->{ship}. Skipping.");
	    return undef;
	}
	if ($donor->{secreturl} =~ /\.gz$/) {
	    $content = uncompress_string($content);
	}
	$content =~ s/Keep secret URL \S+/Keep secret URL DontCheat/g;
	$fh = new FileHandle(">$fname") or
	    error("Couldn't write $donor->{ship} turn to turn cache $fname");
	print $fh "$content";
	$fh->close();
    } else {
	message("Retrieving $donor->{ship} from turn cache");
	$content = myget("file:$fname");
	if (!defined($content)) {
	    error("Couldn't retrieve turn $Turn from cache for $donor->{ship} id $donor->{donorid}");
	}
    }
    return $content;
}

# Uncompress gzipped string.
# Just write to a file, decompress, read...
sub uncompress_string {
    my($str) = @_;
    my($fname, $fh, $oldrs);
    $fname = "/var/tmp/uncompresss_string.$$";
    $fh = new FileHandle(">$fname.gz") or error("Couldn't write to $fname.gz");
    print $fh "$str";
    $fh->close();
    system("gunzip $fname.gz");
    $fh = new FileHandle("$fname") or error("Couldn't open $fname");
    $oldrs = $/;	# I don't think I have to do this.
    undef $/;
    $str = <$fh>;
    $fh->close();
    $/ = $oldrs;
    unlink($fname);
    return $str;
}

sub GetTerminalReport {
    my($data, $url) = @_;
    return GetReport("terminal report", "tr", $data, $url);
}

sub GetPresReport {
    my($data, $url) = @_;
    return GetReport("presidential report", "pr", $data, $url);
}

sub GetReport {
    my($label, $code, $data, $url) = @_;

    my($donor, $donorid, $fname, $content, $turn);
    $donor = $data->{donor};
    $donorid = $donor->{donorid};
    $turn = $data->{turn};
    $fname = "$Top/turns/$turn/$donorid.$code.html";
    if (!-e "$Top/turns/$turn") {
	message("Making turn cache directory $Top/turns/$turn");
	mkdir("$Top/turns/$turn");
    }
    if (! -r $fname) {
	if ($CacheOnly) {
	    warning("Temporarily only using cache for $label");
	    return undef;
	}
	message("Downloading $label for $donor->{ship} from $url");
	if (!mygetstore($url, $fname)) {
	    error("Unable to getstore $url for $label for $donor->{ship}");
	}
    } else {
	message("Retrieving $label for $donor->{ship} from turn cache");
    }
    $content = myget("file:$fname");
    if (!defined($content)) {
	error("Couldn't retrieve turn $turn from cache for $label for $donor->{ship}");
    }
    return $content;
}

#
# Download a ship from the tbg server OR retrieve it from the cache
# if it is already there.
# 
# Update the shipconfig table.
#

sub GetShip {
    my($data, $ship, $url) = @_;
    my($fname, $content, $shipfname, $turn, $donor, $donated, $purgers);

    $donor = $data->{donor};
    $turn = $data->{turn};

    # Make the directory if necessary
    if (!-e "$Top/ships/$turn") {
	message("Making ship cache directory $Top/ships/$turn");
	mkdir("$Top/ships/$turn");
    }

    # Get a file name that can be stored. Horrible hack.
    $shipfname = $ship;
    $shipfname =~ s/[^a-zA-Z0-9]//g;
    $fname = "$Top/ships/$turn/$shipfname.html";

    # If in the table, it should be in the cache
    if (ExistsSelect("select * from shipconfig where ship=? and turn=? and path=?;", 
		     $ship, $turn, $fname)) {
	if (! -r $fname) {
	    error("Couldn't find cached ship config for $ship in $fname");
	}
	if ($donor->{shipconfig}) {
	    mydo("update shipconfig set donated=true where ship=? and turn=? and path=?;",
 		 $ship, $turn, $fname);
	}
	if ($donor->{purgers}) {
	    mydo("update shipconfig set purgers=true where ship=? and turn=? and path=?;",
 		 $ship, $turn, $fname);
	}
    } else {

	# If we get here, it is not in the table. It should not be in the cache either
    
	if ($CacheOnly) {
	    warning("Couldn't load $ship. Currently, only using cache for ship configs"); #!!!
	    return undef;
	}
	
	if (-r $fname) {
	    error("Found $ship in cache at $fname, but not in table");
	}
	
	message("Downloading $ship from $url");
	if (!mygetstore($url, $fname)) {
	    error("unable to getstore $url for $ship");
	}

	mydo("insert into shipconfig values(?, ?, ?, false, false);", $ship, $fname, $turn);
	if ($donor->{shipconfig}) {
	    mydo("update shipconfig set donated=true where ship=? and turn=?;", $ship, $turn);
	}
	if ($donor->{purgers}) {
	    mydo("update shipconfig set purgers=true where ship=? and turn=?;", $ship, $turn);
	}

    }

    $content = myget("file:$fname");
    if (!defined($content)) {
	error("Couldn't retrieve turn $turn from cache for $ship ($fname)");
    }
    message("Retrieving $ship from cache");
    return $content;
}

sub UpdateTurns {
    my($sth, $donor);
    $sth = mydo("select * from donors where secreturl != '';");
    while ($donor = $sth->fetchrow_hashref()) {
	if (defined($donor->{secreturl}) && $donor->{secreturl} !~ /^\s*$/) {
	    UpdateTurn($donor);
	}
    }
    $sth->finish();
}

sub UpdateTerminalReport {
    my($donordata, $url) = @_;
    my($donor, %data, $content, $fh, $done);
    $donor = $donordata->{donor};
    message("\nTerminal report from $donor->{ship}");
    $data{is_terminal_report} = 1;
    $data{donor} = $donor;
    $data{turn} = $donordata->{turn};
    $data{engskill} = $donordata->{engskill};
    $data{sciskill} = $donordata->{sciskill};
    $data{medskill} = $donordata->{medskill};
    $data{weapskill} = $donordata->{weapskill};
    $content = GetTerminalReport($donordata, $url);
    if (!defined($content)) {
	warning("Unable to fetch terminal report by $donor->{ship} at $url");
	return;
    }
    $fh = new IO::Scalar \$content;
    $data{fh} = $fh;
    $done = 0;
    while (!$done) {
	HandleSystem(\%data);   # Includes trade goods
	HandleShips(\%data);
	$done = HandleShops(\%data);
    }
    $fh->close();
    message("End of terminal report from $donor->{ship}\n");
}

# Given the name of the presidents ship and the URL to the pres
# report, update the database with the report. This is for when the
# president sends his URL, but isn't a "real" DOW member. His
# membership information is put in the donors table, but the secret
# URL is blank, so it will not be downloaded by UpdateTurns.
#
# (I added a call to this function by hand when this happened)

sub UpdatePres {
    my($presship, $url) = @_;
    my($donor, %data);
    $donor = SelectOneRowAsHash("select * from donors where ship=?;", $presship);
    $data{donor} = $donor;
    $data{turn} = $Turn;
    $data{engskill} = 0;
    $data{sciskill} = 0;
    $data{medskill} = 0;
    $data{weapskill} = 0;
    message("Updating Presidential Report from command line for $presship on $Turn from $url");
    UpdatePresReport(\%data, $url);
}    

sub UpdatePresReport {
    my($donordata, $url) = @_;
    my($donor, %data, $content, $fh, $done, %newdonor, $key);
    $donor = $donordata->{donor};

    # Copy President's personal settings...
    foreach $key (keys %{$donor}) {
	$newdonor{$key} = $donor->{$key};
    }

    # Presidential sharing preferences. Uncomment to override
    # President's personal settings. (I did this at the request of the president.)

    # Note: the adv_ probably don't matter.
#    $newdonor{adv_newbie} = 0;
#    $newdonor{adv_done} = 0;
#    $newdonor{adv_high} = 0;
#    $newdonor{adv_hard} = 0;
#    $newdonor{adv_all} = 0;
#    $newdonor{shipconfig} = 0;
#    $newdonor{shiploc} = 0;
#    $newdonor{influence} = 0;

    $data{donor} = \%newdonor;
    $data{is_pres_report} = 1;
    $data{turn} = $donordata->{turn};
    $data{engskill} = $donordata->{engskill};
    $data{sciskill} = $donordata->{sciskill};
    $data{medskill} = $donordata->{medskill};
    $data{weapskill} = $donordata->{weapskill};

    message("\nPresidential report from $donor->{ship}");
    $content = GetPresReport($donordata, $url);
    if (!defined($content)) {
	warning("Unable to fetch presidential report by $donor->{ship} at $url");
	return;
    }
    $fh = new IO::Scalar \$content;
    $data{fh} = $fh;
    $done = 0;
    while (!$done) {
	HandleSystem(\%data);   # Includes trade goods
	HandleShips(\%data);
	$done = HandleShops(\%data);
    }
    $fh->close();
    message("End of presidential report from $donor->{ship}\n");
}

sub UpdateTurn {
    my($donor) = @_;
    my($content, $fh, $turn);
    my(%data);

    $data{donor} = $donor;
    $data{is_terminal_report} = 0;

    message("\n\nUpdating turn $Turn for $donor->{ship}");
    if (ExistsTurnUpdate($donor, $Turn)) {
	warning(" Turn $Turn for $donor->{ship} already exists. Skipping.");
	return;
    }
    message("Turn $Turn for $donor->{ship} does not exist. Fetching.");
    # Get the turn information. Updates the cache.
    $content = GetTurn($donor);

    if (!defined($content) || $content =~ /^\s*$/) {
	warning(" Unable to fetch $donor->{secreturl}, turn $Turn for $donor->{ship}.");
	return;
    }

    if ($content =~ /^<HTML><HEAD><TITLE>To Boldly Go, Turn ([0-9]+)<\/TITLE>/) {
	$turn = $1;
	if ($Turn != $turn) {
	    warning("Expected turn $Turn for $donor->{ship} ($donor->{donorid} $donor->{email}). Got turn $turn.");
	    # If we got the wrong turn, just fail, since other data such
	    # as ship pages may not be available.
	    return;
	}
    } else {
	error("Couldn't find turn for $donor->{ship} in $donor->{secreturl}");
    }

    $data{turn} = $turn;

    # Once we get here, $content should have a valid turn we haven't seen.
    # The valid turn is $turn, not $Turn.

    UpdateTurnUpdate($donor, $turn);

    # Create a new entry for ship data.
    mydo("insert into shipdata values(default, ?, ?);", $donor->{donorid}, $turn);
    message("Creating shipdata for $donor->{ship} turn $turn");
    $data{shipdataid} = GetSequence('shipdata_shipdataid');

    $fh = new IO::Scalar \$content;
    $data{fh} = $fh;

    HandleSkills(\%data);
    HandleAdventures(\%data);
    HandleTerminals(\%data);
    HandlePlagues(\%data);
    HandleCriminals(\%data);
    HandleEnemies(\%data);
    HandleSystem(\%data);   # Includes trade goods
    HandleShips(\%data);
    HandleShops(\%data);
    HandleFavour(\%data);
    HandlePolitics(\%data);

    HandleOrders(\%data);
    
    $fh->close();

    # If the URL has a terminal report embedded, call it.

    if ($content =~ m|<A HREF="http://tbg.fyndo.com/tbg/(.*).htm">Starnet Terminal Report</A>|) {
	UpdateTerminalReport(\%data, "http://tbg.fyndo.com/tbg/$1.htm");
    }

    # If the URL has a presidential report embedded, call it.
    # (This is updated by hand depending on what the current pres wants to do)
#    if ($content =~ m|<A HREF="http://tbg.fyndo.com/tbg/(.*).htm">Report from Alien ships</A>|) {
#	UpdatePresReport(\%data, "http://tbg.fyndo.com/tbg/$1.htm");
#    }
} # UpdateTurn()

# 
# Detect if influence has degraded to zero. If so, enter a 0 votes line.
#

sub FixupInfluence {
    my($sth, $row, @donorships);

    message("Fixing up influence");
    mydo("delete from influence where ship='Unknown' and turn=$Turn;");

    @donorships = SelectAll("select ship from donors where secreturl != '';");

    # The next line could be more efficient if I could just remember what it did... :-)
    $sth = mydo("select i1.* from influence i1 left join influence i2 on (i1.turn<i2.turn and i1.system=i2.system and i1.race=i2.race and i1.location=i2.location) where i2.turn is null and i1.turn<? and (" . join(' or ', map { "i1.ship=?" } @donorships) . ");", $Turn, @donorships);
    
    while ($row = $sth->fetchrow_hashref()) {
	message("Noticed that $row->{ship} influence at $row->{system} $row->{race} $row->{location} has gone to zero.");
	if (!ExistsSelect("select * from influence where system=? and race=? and location=? and votes=? and turn=?;", $row->{system}, $row->{race}, $row->{location}, $row->{votes}, $Turn)) {
	    message(" No data replaced it. Inserting an Unknown entry.");
	    mydo("insert into influence values(?, ?, ?, ?, ?, ?, ?, ?);",
		 "Unknown", $row->{system}, $row->{race}, $row->{location},
		 $row->{votes}, 0, $Turn, SelectOne("select influence from donors where ship=?;",
						    $row->{ship}));
	} else {
	    message("Some other entry replaced it.");
	}
    }
    $sth->finish();
}

sub ProcessProbeReport {
    my($donordata) = @_;
    my($donor, %data);
    $donor = $donordata->{donor};
    message("\nProbe report from $donor->{ship}");
    $data{is_probe_report} = 1;
    $data{donor} = $donor;
    $data{turn} = $donordata->{turn};
    $data{fh} = $donordata->{fh};
    $data{engskill} = $donordata->{engskill};
    $data{sciskill} = $donordata->{sciskill};
    $data{medskill} = $donordata->{medskill};
    $data{weapskill} = $donordata->{weapskill};
    HandleSystem(\%data);
    HandleShips(\%data);
    HandleShops(\%data);
    message("End of probe report from $donor->{ship}\n");
}

sub HandleFavour {
    my($data) = @_;
    my($line, $fh, $area, $favour, $donor);
    $fh = $data->{fh};
    $donor = $data->{donor};
    for (;;) {
	$line = trim(getline($fh));
	if ($line =~ m|<h3>Politics</h3>|) {
	    return;
	}
	if ($line =~ m|<P>Starnet Terminal reveals password fragment (.*)$|) {
	    ProcessFragment($data, $1);
	} elsif ($line =~ m|<HR><H1>View from Probe</H1>|) {
	    ProcessProbeReport($data);
	} elsif ($line =~ m|<P>Tracer shows (.*?) is at (.*?)\s*$|) {
	    ProcessTracer($data, $1, $2);
	} elsif ($line =~ m|<H1>View from Tracer</H1>|) {
	    ProcessTraceReport($data);
	} elsif ($line =~ m/<LI>(Engineering|Science|Medical|Weaponry):\s*([0-9]+)/) {
	    $area = $1;
	    $favour = $2;
	    message("setting $area favour to $favour");
	    mydo("insert into favour values(?, ?, ?, ?);",
		 $donor->{donorid}, $data->{turn}, $area, $favour);
	}
    }
}

sub HandlePolitics {
    my($data) = @_;
    my($line, $fh, $donor);
    $fh = $data->{fh};
    $donor = $data->{donor};

    for (;;) {
	$line = trim(getline($fh));
	if ($line eq '<h3>Finances</h3>') {
	    return;
	}
	# As of turn 1542, the finances section is missing for ships at the holiday planet.
	if ($line eq '<FORM ACTION="http://tbg.fyndo.com/tbg/tbgmail.cgi" METHOD="POST">') {
	    return;
	}
	# As of turn 1566, the format of the submit form changed for shared urls.
	if ($line =~ m|<P>\(ending turn at star system Holiday Planet|) {
	    return;
	}
	if ($line =~ m|<td>(.*?) colony \(([0-9]+)\) at (.*?)</td><td>([0-9]+)|) {
	    AddInfluence($data, $donor->{ship}, $1, $2, 1, $4, $3);
	} elsif ($line =~ m|<td>(.*?) homeworld \(([0-9]+)\) at (.*?)</td><td>([0-9]+)|) {
	    AddInfluence($data, $donor->{ship}, $1, $2, 6, $4, $3);
	}   
    }
}
	    
sub ProcessTraceReport {
    my($donordata) = @_;
    my($donor, %data);
    $donor = $donordata->{donor};
    message("\nTrace report from $donor->{ship}");
    $data{is_trace_report} = 1;
    $data{donor} = $donor;
    $data{turn} = $donordata->{turn};
    $data{fh} = $donordata->{fh};
    $data{engskill} = $donordata->{engskill};
    $data{sciskill} = $donordata->{sciskill};
    $data{medskill} = $donordata->{medskill};
    $data{weapskill} = $donordata->{weapskill};
    HandleSystem(\%data);
    HandleShips(\%data);
    HandleShops(\%data);
    message("End of trace report from $donor->{ship}\n");
}
   
    
sub ProcessTracer {
    my($data, $ship, $loc) = @_;
    my($donor);
    $donor = $data->{donor};
    $loc =~ s/^Holiday Planet for.*$/Holiday Planet/;

    message("Tracer shows $ship is at $loc");
    
    if (!ExistsSelect("select * from shiploc where ship=? and turn=? and system=?;", $ship, $data->{turn}, $loc)) {
	mydo("insert into shiploc values (?, ?, ?, false, false);",
	     $loc, $data->{turn}, $ship);
    }
    
    if ($donor->{shiploc}) {
	mydo("update shiploc set donated=true where ship=? and turn=? and system=?;", $ship, $data->{turn}, $loc);
    }

    if ($donor->{purgers}) {
	mydo("update shiploc set purgers=true where ship=? and turn=? and system=?;", $ship, $data->{turn}, $loc);
    }

    mydo("insert into traces values(?, ?, ?);",
	 $donor->{donorid}, $ship, $data->{turn});
}


sub ProcessFragment {
    my($data, $frag) = @_;
    if (!ExistsSelect("select * from fragments where turn=? and fragment=?;", 
		      $data->{turn}, $frag)) {
	mydo("insert into fragments values (?, ?, ?);",
	     $data->{turn}, $frag, "DOW");
	message("Starnet terminal fragment $frag (entered)");
    } else {
	message("Starnet terminal fragment $frag (confirmed)");
    }
}
    

sub HandleSkills {
    my($data) = @_;
    HandleSkillSummary($data);
    HandleCrew($data);
    HandleSkillDetails($data);
} # HandleSkills()

sub HandleSkillSummary {
    my($data) = @_;
    my($line, $fh);
    $fh = $data->{fh};
    for (;;) {
	$line = getline($fh);
	if ($line =~ /^<TR><TH>Engineering skills \(([0-9]+)/) {
	    $data->{engskill} = $1;
	    mydo("update shipdata set engskill=? where shipdataid=?;", $data->{engskill}, $data->{shipdataid});
	    message("Setting Engineering skill to $data->{engskill}");

	    $line = getline($fh);
	    if ($line =~ /^<TH>Science skills \(([0-9]+)/) {
		$data->{sciskill} = $1;
		mydo("update shipdata set sciskill=? where shipdataid=?;", $data->{sciskill}, $data->{shipdataid});
		message("Setting Science skill to $data->{sciskill}");
	    } else {
		error("Expected science line, got $line");
	    }

	    $line = getline($fh);
	    if ($line =~ /^<TH>Medical skills \(([0-9]+)/) {
		$data->{medskill} = $1;
		mydo("update shipdata set medskill=? where shipdataid=?;", $data->{medskill}, $data->{shipdataid});
		message("Setting Medical skill to $data->{medskill}");
	    } else {
		error("Expected medical line, got $line");
	    }

	    $line = getline($fh);
	    if ($line =~ /^<TH>Weaponry skills \(([0-9]+)/) {
		$data->{weapskill} = $1;
		mydo("update shipdata set weapskill=? where shipdataid=?;", $data->{weapskill}, $data->{shipdataid});
		message("Setting Weaponry skill to $data->{weapskill}");
	    } else {
		error("Expected weaponry line, got $line");
	    }
	    return;
	}
    }
} # HandleSkillSummary()

sub HandleCrew {
    my($data) = @_;
    my($line, $ncrew, $crewskill, $fh);

    $fh = $data->{fh};
    
    while ($line = getline($fh)) {
	if ($line =~ /^<\/TR><TR ALIGN=CENTER><TD>([0-9]+) crew, average skill: ([0-9]+)<\/TD>$/) {
	    $ncrew = $1;
	    $crewskill = $2;
	    mydo("update shipdata set nengcrew=? where shipdataid=?;", $ncrew, $data->{shipdataid});
	    mydo("update shipdata set engcrewskill=? where shipdataid=?;", $crewskill, $data->{shipdataid});
	    message("Setting Engineering crew to $ncrew and skill to $crewskill");

	    $line = getline($fh);
	    if ($line =~ /^<TD>([0-9]+) crew, average skill: ([0-9]+)<\/TD>$/) {
		$ncrew = $1;
		$crewskill = $2;
		mydo("update shipdata set nscicrew=? where shipdataid=?;", $ncrew, $data->{shipdataid});
		mydo("update shipdata set scicrewskill=? where shipdataid=?;", $crewskill, $data->{shipdataid});
		message("Setting Science crew to $ncrew and skill to $crewskill");
	    } else {
		error("Failed to find science crew");
	    }

	    $line = getline($fh);
	    if ($line =~ /^<TD>([0-9]+) crew, average skill: ([0-9]+)<\/TD>$/) {
		$ncrew = $1;
		$crewskill = $2;
		mydo("update shipdata set nmedcrew=? where shipdataid=?;", $ncrew, $data->{shipdataid});
		mydo("update shipdata set medcrewskill=? where shipdataid=?;", $crewskill, $data->{shipdataid});
		message("Setting Medical crew to $ncrew and skill to $crewskill");
	    } else {
		error("Failed to find medical crew");
	    }

	    $line = getline($fh);
	    if ($line =~ /^<TD>([0-9]+) crew, average skill: ([0-9]+)<\/TD>$/) {
		$ncrew = $1;
		$crewskill = $2;
		mydo("update shipdata set nweapcrew=? where shipdataid=?;", $ncrew, $data->{shipdataid});
		mydo("update shipdata set weapcrewskill=? where shipdataid=?;", $crewskill, $data->{shipdataid});
		message("Setting Weaponry crew to $ncrew and skill to $crewskill");
	    } else {
		error("Failed to find weaponry crew");
	    }
	    return;
	}
    }
} # HandleCrew()

sub HandleSkillDetails {
    my($data) = @_;
    my($line, $fh);
    
    $data->{skillindex} = 0;
    $fh = $data->{fh};
    while ($line = getline($fh)) {
	if ($line =~ /<TD>(.*)<\/TD>/) {
	    ProcessSkill($data, $1);
	} elsif ($line =~ /<\/TR><\/TABLE>/) {
	    return;
	} else {
	    error("Found unexpected line $line while processing skills");
	}		
    }
    error("Unexpected end of file while processing skill details");
} # HandleSkillDetails()

sub ProcessSkill {
    my($data, $name) = @_;
    my($donor, $donorid, $turn, $area);
    
    $donor = $data->{donor};
    $donorid = $donor->{donorid};
    $area = (qw( Engineering Science Medical Weaponry))[$data->{skillindex}];
    $data->{skillindex} = $data->{skillindex} + 1;
    if ($data->{skillindex} >= 4) {
	$data->{skillindex} = 0;
    }

    if ($name =~ /^\s*$/) {
	return;
    }
   
    # Check if already in table.
    if (!CheckForSkill($donorid, $area, $name)) {
	mydo("insert into skills values(?, ?, ?, ?);", $donorid, $data->{turn}, $area, $name);
	message("Setting $area skill $name (skill inserted)");
    } else {
	message("Setting $area skill $name (already existed)");
    }
}  # ProcessSkill()

sub HandleAdventures {
    my($data) = @_;
    my($line, $fh, $donor);
    $donor = $data->{donor};
    $fh = $data->{fh};
    $line = trim(getline($fh));
    if ($line ne '<H2><A HREF="http://tbg.fyndo.com/tbg/Rules.html#Adventures">Adventures</A> Known at:</H2>') {
	error("Couldn't find adventures for $donor->{ship} (got '$line')");
    }
    for (;;) {
	$line = trim(getline($fh));
	if ($line eq '<H2><A HREF="http://tbg.fyndo.com/tbg/Rules.html#Terminals">Terminals</A> Accessed at:</H2>') {
	    return;
	}
	if ($line =~ m|^<LI>(.*?)-([0-9]+) \((.*?)\) in .*?-([0-9]+) at (.*?)<BR>$|) {
	    ProcessAdventure($data, $1, $2, $3, $5, undef, $4);
	} else {
	    error("Unexpected line $line while processing adventures");
	}
    }
}

sub ProcessAdventure {
    my($data, $area, $level, $name, $system, $sensor, $locid) = @_;
    my($sth, $row, $shiplevel, $advid, $donor);
    my($ptsth, $ptrow);
    $donor = $data->{donor};

    message("$donor->{ship} reports $area-$level $name at $system on turn $data->{turn}");
    
    # Check if it exists
    $sth = mydo("select advid from adventures where area=? and level=? and name=? and system=? and turn=?;", $area, $level, $name, $system, $data->{turn});
    $row = $sth->fetchrow_hashref();
    if (defined($row) && exists($row->{advid}) && defined($row->{advid})) {
	$advid = $row->{advid};
	$sth->finish();
    } else {
	mydo("insert into adventures values (default, ?, ?, ?, ?, ?);", $area, $level, $name, $system, $data->{turn});
	$advid = GetSequence('adventures_advid');
    }

    if ($area eq 'Engineering') {
	$shiplevel = $data->{engskill};
    } elsif ($area eq 'Medical') {
	$shiplevel = $data->{medskill};
    } elsif ($area eq 'Science') {
	$shiplevel = $data->{sciskill};
    } elsif ($area eq 'Weaponry') {
	$shiplevel = $data->{weapskill};
    } else {
	error("Unexpected area for adventure '$area'");
    }
    if (!defined($shiplevel)) {
	error("Shiplevel for $area not defined for $donor->{ship} id $donor->{donorid}");
    }

    # For historic reasons, locid is updated here. In previous versions, it wasn't always set.

    if (defined($locid)) {
	mydo("update adventures set locid=? where advid=?;", $locid, $advid);
    } else {
	error("The locid was not set in ProcessAdventure");
    }
	
    # Update sensors
    # If provided as args, use it.
    # Otherwise, check the previous turn and use it if it exists.

    if (defined($sensor)) {
	mydo("update adventures set sensors=? where advid=?;", $sensor, $advid);
    } else {
	$ptsth = mydo("select * from adventures where area=? and level=? and name=? and system=? and turn=? and sensors is not null;", 
		      $area, $level, $name, $system, $data->{turn}-1);
	$ptrow = $ptsth->fetchrow_hashref();
	if (defined($ptrow) && 
	    exists($ptrow->{sensors}) && defined($ptrow->{sensors}) && 
	    $ptrow->{sensors} =~ /^[0-9]+$/) {
	    mydo("update adventures set sensors=? where advid=?;", $ptrow->{sensors}, $advid);
	}
	$ptsth->finish();
    }

    if ($donor->{adv_all}) {
	mydo("update adventures set adv_all=true where advid=?;", $advid);
    }
    if ($level <= 5 && $donor->{adv_newbie}) {
	mydo("update adventures set adv_newbie=true where advid=?;", $advid);
    }
    if ($level <= 4 && $donor->{pub_adv_newbie}) {
	mydo("update adventures set pub_adv_newbie=true where advid=?;", $advid);
    }
    if ($level >= 25 && $donor->{adv_hard}) {
	mydo("update adventures set adv_hard=true where advid=?;", $advid);
    }
    if ($level > $shiplevel+1 && $donor->{adv_high}) {
	mydo("update adventures set adv_high=true where advid=?;", $advid);
    }
    if (CheckForSkill($donor->{donorid}, $area, $name) && $donor->{adv_done}) {
	mydo("update adventures set adv_done=true where advid=?;", $advid);
    }
}

sub HandleTerminals {
    my($data) = @_;
    my($donor, $fh, $line);
    $donor = $data->{donor};
    $fh = $data->{fh};
    
    for (;;) {
	$line = trim(getline($fh));
	if ($line eq '<H2><A HREF="http://tbg.fyndo.com/tbg/Rules.html#Cure">Plagues</A> Cured at:</H2>') {
	    return;
	}
	message("Terminal $line hacked on turn $data->{turn}");
	mydo("insert into terminals values(?, ?, ?);", 
	     $donor->{donorid}, $line, $data->{turn});
    }
}

sub HandlePlagues {
    my($data) = @_;
    my($donor, $fh, $line);
    $donor = $data->{donor};
    $fh = $data->{fh};
    
    for (;;) {
	$line = trim(getline($fh));
	if ($line eq '<H2><A HREF="http://tbg.fyndo.com/tbg/Rules.html#Criminals">Criminals</A> Known:</H2>') {
	    return;
	}
	message("Plague $line cured on turn $data->{turn}");
	mydo("insert into plagues values(?, ?, ?);", 
	     $donor->{donorid}, $line, $data->{turn});
    }
}

sub HandleCriminals {
    my($data) = @_;
    my($donor, $fh, $line, $who, $level, $loc, $system);
    $donor = $data->{donor};
    $fh = $data->{fh};
    
    for (;;) {
	$line = getline($fh);
	chop($line);
	if ($line eq '<H2>Your <A HREF="http://tbg.fyndo.com/tbg/Rules.html#Aliens">Enemies</A> are:</H2>') {
	    return;
	}
	if ($line =~ m|^<BR>(.*?) (.*?) in (.*?) at (.*?)$|) {
	    $who = $1;
	    $level = $2;
	    $loc = $3;
	    $system = $4;
	    message("Criminal $who:$level:$loc:$system");
	    # If it doesn't already exist, create it.
	    if (!ExistsSelect("select who from criminals where who=? and level=? and location=? and system=? and turn=?;", 
			      $who, $level, $loc, $system, $data->{turn})) {
		mydo("insert into criminals values(?, ?, ?, ?, ?);", 
		     $who, $level, $loc, $system, $data->{turn});
	    }
	} elsif ($line =~ m|^<BR>.*in captivity$|) {
	    # nothing
	} else {
	    error("Unexpected line in criminals $line");
	}
    }
}

sub HandleEnemies {
    my($data) = @_;
    my($donor, $fh, $line);
    $donor = $data->{donor};
    $fh = $data->{fh};
    
    for (;;) {
	$line = trim(getline($fh));
	# If any tag, unget it and allow the next thing to process.
	if ($line =~ m|^<|) {
	    ungetline($line);
	    return;
	}
	message("Enemy $line");
	mydo("insert into enemies values(?, ?, ?);", 
	     $donor->{donorid}, $line, $data->{turn});
    }
}

sub HandleSystem {
    my($data) = @_;
    HandleSystemSector($data);
    HandleSystemLocations($data); # Trade goods, rogue bands, votes, etc
}

sub HandleSystemSector {
    my($data) = @_;
    my($donor, $fh, $line, $system, $plague);
    $donor = $data->{donor};
    $fh = $data->{fh};
    for (;;) {
	$line = getline($fh);
	if ($line =~ m|^<A NAME=\"([^\"]+)\"></A><H1>Sector.*Star system (.*) \(.*\).*:<\/H1>$|) {
	    $system = $1;
	    if ($system ne $2) {
		error(" Strange mismatch in system names");
	    }
	    if ($system =~ /Holiday Planet/) {
		$system = 'Holiday Planet';
	    }
	    if ($data->{is_terminal_report}) {
		message("\nProcessing $system from terminal report");
	    } elsif ($data->{is_trace_report}) {
		message("\nProcessing $system from trace report");
	    } elsif ($data->{is_probe_report}) {
		message("\nProcessing $system from probe report");
	    } elsif ($data->{is_pres_report}) {
		message("\nProcessing $system from presidential report");
	    } else {
		message("Processing $system");
	    }

	    $data->{system} = $system;
	    if ($line =~ m|Plague at ([0-9]+)%|) {
		$plague = $1;
		mydo("update sysplagues set level=? where system=?;",
		     $plague, $system);
		mydo("update sysplagues set turn=? where system=?;",
		     $data->{turn}, $system);
	    }
	} elsif ($line =~ m|^<H2>Locations in this system</H2>|) {
	    return;
	}
    }
} # HandleSystemSector

sub HandleSystemLocations {
    my($data) = @_;
    my($line, $fh);
    $fh = $data->{fh};
    $line = trim(getline($fh));
    if ($line ne '<TABLE BORDER=1><TR><TH>Id</TH><TH>Description</TH></TR>') {
	error("Expected table heading for Locations, got $line.");
    }
    for (;;) {
	$line = trim(getline($fh));
	if ($line eq '</TABLE>') {
	    return;
	}
	if ($line =~ m|^<TR><TD>([0-9]+)</TD><TD>(.*)$|) {
	    ProcessLocation($data, $1, $2);
	} elsif ($line =~ m|^\s*$|) {
	    # Nothing
	} else {
	    error("Unexpected line while handling system locations $line");
	}
    }
}

sub ProcessLocation {
    my($data, $locid, $desc) = @_;
    my($resource, $price, $donor, $trade_donorid);
    $donor = $data->{donor};
    $trade_donorid = $donor->{donorid};
    if ($data->{is_terminal_report}) {
	$trade_donorid += 1000;		# Eww, horrible.
    }
    if ($data->{is_trace_report}) {
	$trade_donorid += 2000;
    }
    if ($data->{is_pres_report}) {
	$trade_donorid += 3000;
    }

    # Handle colony buying stuff...
    if ($desc =~ /buying (.*?) for \$([0-9]+) /) {
	$resource = $1;
	$price = $2;
	if (!SystemBuysResource($data->{system}, $resource)) {
	    error("$donor->{ship} appears to be cheating. $data->{system} does not buy $resource.");
	}
	if (ExistsTradePrice($data->{system}, $resource, $price, $data->{turn}, $trade_donorid)) {
	    message("$resource for \$$price (confirmed)");
	} else {
	    mydo("insert into trade values(default, ?, ?, ?, ?, ?, ?);",
		 $data->{system}, $resource, $price, $data->{turn}, $trade_donorid, $locid);
	    message("$resource for \$$price (entered)");
	}
	if ($donor->{pub_trade}) {
	    mydo("update trade set pub_shared=true where system=? and resource=? and price=? and turn=? and locid=?;", $data->{system}, $resource, $price, $data->{turn}, $locid);
	}
    } elsif ($desc =~ m|Badland, danger ([0-9]+)% \(([a-z]+) ([a-z]+) rogue band\)|i) {
	AddRogueBand($data->{system}, $2, $3, 'Life Support', $1, $data->{turn});
    } elsif ($desc =~ m|Gas Giant, danger ([0-9]+)% \(([a-z]+) ([a-z]+) rogue band\)|i) {
	AddRogueBand($data->{system}, $2, $3, 'Impulse', $1, $data->{turn});
    }

    # Handle colony and homeworld influence
    if ($desc =~ m|(.*?) Colony.*1 (.*?) vote \((.*?) has ([0-9]+) influence\)|) {
	#          race            area          ship      infl
	AddInfluence($data, $3, $1, $locid, 1, $4, $data->{system});
    } elsif ($desc =~ m|(.*?) Homeworld.*6 (.*?) votes \((.*?) has ([0-9]+) influence\)|) {
	AddInfluence($data, $3, $1, $locid, 6, $4, $data->{system});
    }

    # Handle adventures
    if ($desc =~ m|\s*(.*?) in (.*?), needs skill ([0-9]+) \(([0-9]+)%\)|) {
	ProcessAdventure($data, $2, $3, $1, $data->{system}, $4, $locid);
    }

    # Handle good/evil rings
    if ($desc =~ /\((.*?) (.*?) Ring\)/) {
	ProcessRing($data, $1, $2, $data->{system}, $locid);
    }
} # ProcessLocation

sub ProcessRing {
    my($data, $type, $area, $system, $locid) = @_;
#    warning("Noticed $type $area Ring in $system at locid $locid");
    mydo("insert into rings values (?, ?, ?, ?);",
	 $type, $area, $system, $data->{turn});
}

sub AddInfluence {
    my($data, $ship, $race, $location, $votes, $influence, $system) = @_;
    my($turn, $donor);
    $turn = $data->{turn};
    $donor = $data->{donor};

    if (!ExistsSelect("select ship from influence where ship=? and system=? and race=? and location=? and votes=? and influence=? and turn=?;", $ship, $system, $race, $location, $votes, $influence, $turn)) {
	mydo("insert into influence values (?, ?, ?, ?, ?, ?, ?, false);",
	     $ship, $system, $race, $location, $votes, $influence, $turn);
	message("$ship has $votes votes and $influence influence over $race at $system $location (added)");
    } else {
	message("$ship has $votes votes and $influence influence over $race at $system $location (confirmed)");
    }
    
    if ($donor->{influence}) {
	mydo("update influence set donated=true where ship=? and system=? and race=? and location=? and votes=? and influence=? and turn=?;", $ship, $system, $race, $location, $votes, $influence, $turn);
    }
}
    
#
# Check if the given system/resource/turn has already been
# entered. If so, confirm the prices are the same, and return 1.
# If not, return 0.
#

sub ExistsTradePrice {
    my($system, $resource, $price, $turn, $donorid) = @_;
    my($sth, $oldprice, $row, $gotone);
    $sth = mydo("select price, donorid from trade where system=? and resource=? and turn=?;", $system, $resource, $turn);
    $gotone = 0;
    while ($row = $sth->fetchrow_hashref()) {
	next if $row->{donorid} == $donorid;
	$gotone = 1;
	if ($row->{price} == $price) {
	    $sth->finish();
	    return 1;
	}
    }
    if ($gotone) {
	error("Price conflict! $system $resource $turn $price");
    }
    $sth->finish();
    return 0;
}

sub insert_popcorn {
    my($data, $impulse, $sensor, $shield) = @_;
    my($sth, $row);
    $sth = mydo("select * from popcorn where turn=?;", $data->{turn});
    $row = $sth->fetchrow_hashref();

    if (!defined($row)) {
	mydo("insert into popcorn values(?, ?);",
	     $data->{system}, $data->{turn});
	message("Popcorn source at $data->{system} (created)");
	$sth->finish();
	$sth = mydo("select * from popcorn where turn=?;", $data->{turn});
	$row = $sth->fetchrow_hashref();
	if (!defined($row)) {
	    error("Failed to create popcorn entry.");
	}
    }

    if ($row->{system} ne $data->{system}) {
	error("Error in popcorn detection.");
    }
	
    popcorn_update($data, $row, $impulse, "impulse");
    popcorn_update($data, $row, $sensor,  "sensor");
    popcorn_update($data, $row, $shield,  "shield");
}

sub popcorn_update {
    my($data, $row, $val, $lab) = @_;
    
    if (defined($val)) {
	if (exists($row->{$lab}) && defined($row->{$lab})) {
	    if ($row->{$lab} != $val) {
		error("Popcorn $lab mismatch $row->{$lab} vs. $val.");
	    }
	} else {
	    mydo("update popcorn set $lab=? where turn=?;", $val, $data->{turn});
	    message("Updating popcorn $lab to $val");
	}
    }
}


sub HandleShips {
    my($data) = @_;
    my($fh, $line, $ship1, $ship2, $url1, $url2, $rest, $pship, $purl, $pship2, $purl2);
    $fh = $data->{fh};
    $line = trim(getline($fh));
    if ($line !~ m|<H2>Other ships here:</H2>|) {
	error("Couldn't find other ships in system lines");
    }

    # Popcorn is listed on the same line as "Other ships here"

    if ($line =~ m/Popcorn Source: Impulse ([0-9]+)%, Sensor ([0-9]+)%, Shield ([0-9]+)%/) {
	insert_popcorn($data, $1, $2, $3);
    }

    if (!ExistsSelect("select * from systemviewed where system=? and turn=?;",
		      $data->{system}, $data->{turn})) {
	mydo("insert into systemviewed values(?, ?);", 
	     $data->{system}, $data->{turn});
    }
    for (;;) {
	$line = trim(getline($fh));
	if ($line eq '<H3>Details</H3>') {
	    return;
	}
	if ($line =~ m|^<A HREF=\"([^\"]*)\">(.*?)</A>(.*)meets\s*$|) {
	    $url1 = $1;
	    $ship1 = $2;
	    $rest = $3;
	    if ($rest =~ m|\(guarding <A HREF=\"(.*?)\">(.*?)</A>\)|) {
		$purl = $1;
		$pship = $2;
	    } else {
		$purl = ' ';
		$pship = ' ';
	    }
	    $line = trim(getline($fh));
	    if ($line =~ m|^<A HREF=\"(.*?)\">(.*?)</A>(.*)<BR>$|) {
		$url2 = $1;
		$ship2 = $2;
		$rest = $3;
		if ($rest =~ m|\(guarding <A HREF=\"(.*?)\">(.*?)</A>\)|) {
		    $purl2 = $1;
		    $pship2 = $2;
		} else {
		    $purl2 = ' ';
		    $pship2 = ' ';
		}
		ProcessMeeting($data, $ship1, $url1, $ship2, $url2, $pship, $purl, $pship2, $purl2);
	    } else {
		error("Unmatches 'meets' line");
	    }
	} elsif ($line =~ m|^<A HREF=\"(.*?)\">(.*?)</A>(.*)leftover<BR>$|) {
	    $url1 = $1;
	    $ship1 = $2;
	    $rest = $3;
	    if ($rest =~ m|\(guarding <A HREF=\"(.*?)\">(.*?)</A>\)|) {
		$purl = $1;
		$pship = $2;
	    } else {
		$purl = ' ';
		$pship = ' ';
	    }
	    ProcessMeeting($data, $ship1, $url1, ' ', ' ', $pship, $purl, ' ', ' ');
	} else {
	    error("Unexpected line in ship meetings '$line'");
	}
    }
}

sub isset {
    my($str) = @_;
    return defined($str) && $str !~ /^\s*$/;
}

sub ProcessMeeting {
    my($data, $ship1, $url1, $ship2, $url2, $pship, $purl, $pship2, $purl2) = @_;
    my($donor, $system, $turn, $mstr);

    $donor = $data->{donor};
    $system = $data->{system};
    $turn = $data->{turn};

    ProcessShip($data, $ship1, $url1);
    
    $mstr = "$ship1";
    
    if (isset($pship) && isset($purl)) {
	ProcessShip($data, $pship, $purl);
	$mstr .= " (protecting $pship)";
    }

    if (isset($ship2) && isset($url2)) {
	ProcessShip($data, $ship2, $url2);
	$mstr .= " meets $ship2";
	if (isset($pship2) && isset($purl2)) {
	    ProcessShip($data, $pship2, $purl2);
	    $mstr .= " (protecting $pship2)";
	}
    } else {
	$mstr .= " leftover";
    }
    
    if (!ExistsSelect("select system from meetings where system=? and turn=? and ship1=? and ship2=? and protected1=? and protected2=?;", $system, $turn, $ship1, $ship2, $pship, $pship2)) {
	mydo("insert into meetings values(?, ?, ?, ?, false, ?, ?, false);", $system, $turn, $ship1, $ship2, $pship, $pship2);
	message("$mstr (created)");
    } else {
	message("$mstr (confirmed)");
    }
    
    if ($donor->{shiploc}) {
	mydo("update meetings set donated=true where system=? and turn=? and ship1=? and ship2=? and protected1=? and protected2=?;", $system, $turn, $ship1, $ship2, $pship, $pship2);
    }

    if ($donor->{purgers}) {
	mydo("update meetings set purgers=true where system=? and turn=? and ship1=? and ship2=? and protected1=? and protected2=?;", $system, $turn, $ship1, $ship2, $pship, $pship2);
    }
} # ProcessMeeting

# 
# Update ship locations and configurations.
# Extract module percents and pod data for donors only.
#

sub ProcessShip {
    my($data, $ship, $url) = @_;
    my($donor, $content);
    my($warp, $impulse, $sensor, $cloak, $life, $sickbay, $shield, $weapon);
    my($name, $capacity, $res, $n, $i);
    my($tech, $reliability, $yield, $bcre, $bless, $curses, $keys, $artifactid);
    my($race, $value);
    my($flag);

    message("Processing ship $ship");

    $donor = $data->{donor};

    if (!ExistsSelect("select * from shiploc where ship=? and turn=? and system=?;", $ship, $data->{turn}, $data->{system})) {
	mydo("insert into shiploc values (?, ?, ?, false, false);",
	     $data->{system}, $data->{turn}, $ship);
    }

    if ($donor->{shiploc}) {
	mydo("update shiploc set donated=true where ship=? and turn=? and system=?;", $ship, $data->{turn}, $data->{system});
    }

    if ($donor->{purgers}) {
	mydo("update shiploc set purgers=true where ship=? and turn=? and system=?;", $ship, $data->{turn}, $data->{system});
    }

    # Download all ship's data

    $content = GetShip($data, $ship, $url);
    if (!defined($content)) {
	warning("Couldn't get ship data for $ship");
	return;
    }

    # According to SST: In memory of the passing of Arthur C. Clarke, all sufficiently advanced technology has been dimmed galaxy wide. Requiescat in pace.
    # It appears magic modules have <FONT COLOR="#808000">Magic</FONT> around them.
    # 03/20/08

    $content =~ s|<FONT COLOR=\"\#808000\">Magic</FONT>|Magic|g;

    # Extract flag info for players

    if ($ship !~ /[0-9]+$/ && $content =~ m|<TR><TH COLSPAN=4 ALIGN=CENTER>(.*?)</TH></TR>|s) {
	$flag = $1;
	if (!ExistsSelect("select flag from flags where ship=? and turn=?;", $ship, $data->{turn})) {
	    $flag =~ s/\n\)/\)/g;	# Little formatting bug in page
	    mydo("insert into flags (ship, flag, turn) values (?, ?, ?);", $ship, $flag, $data->{turn});
	}
    }
	
    # Only get other data for DOW members
    # I added additional processing of all ship modules in
    # do_ships.pl, which is called from postturn.sh.

    if ($donor->{ship} ne $ship) {
	return;
    }

    # Don't process in reports, since they should already have been
    # processed from the donors turn page. (This is no longer true because
    # you can do the presidential report from the command line! I'm not
    # sure of the right way to do this. Punt until dow2.)

    if ($data->{is_terminal_report} || $data->{is_pres_report} || $data->{is_trace_report}) {
	return;
    }
	
    message("Processing donor information for $ship");

    # Module percents
    if ($content =~ /Warp ([0-9]+)%, Impulse ([0-9]+)%, Sensor ([0-9]+)%, Cloak ([0-9]+)%, Life Support ([0-9]+)%, Sickbay ([0-9]+)%, Shield ([0-9]+)%, Weapon ([0-9]+)%/) {
	$warp = $1;
	$impulse = $2;
	$sensor = $3;
	$cloak = $4;
	$life = $5;
	$sickbay = $6;
	$shield = $7;
	$weapon = $8;
	mydo("update shipdata set impulsepercent = ? where shipdataid=?;",
	     $impulse, $data->{shipdataid});
	mydo("update shipdata set lifesupportpercent = ? where shipdataid=?;",
	     $life, $data->{shipdataid});
	mydo("update shipdata set warppercent = ? where shipdataid=?;",
	     $warp, $data->{shipdataid});
	mydo("update shipdata set sensorpercent = ? where shipdataid=?;",
	     $sensor, $data->{shipdataid});
	mydo("update shipdata set cloakpercent = ? where shipdataid=?;",
	     $cloak, $data->{shipdataid});
	mydo("update shipdata set sickbaypercent = ? where shipdataid=?;",
	     $sickbay, $data->{shipdataid});
	mydo("update shipdata set shieldpercent = ? where shipdataid=?;",
	     $shield, $data->{shipdataid});
	mydo("update shipdata set weaponpercent = ? where shipdataid=?;",
	     $weapon, $data->{shipdataid});
    } else {
	error("Couldn't extract module percents from $ship $url");
    }

    # Pod information
    while ($content =~ m|<TR ALIGN=CENTER><TD>pod-([0-9]+D?)\s*</TD><TD>([0-9]+)</TD><TD>(.*?)</TD><TD>([0-9]+)</TD></TR>|g) {
	$name = "pod-$1";
	$capacity = $2;
	$res = $3;
	$n = $4;
	message("Pod $name $n/$capacity $res");
	mydo("insert into pods values(?, ?, ?, ?, ?, ?);", 
	     $donor->{donorid}, $data->{turn}, $name, $capacity, $n, $res);
    }
    
    # Module information
    
    while ($content =~ /<TR ALIGN=CENTER><TD>(.*?)\s*<\/TD><TD>($TechRE)<\/TD><TD>\s*([0-9]+)%\s*<\/TD><TD>([0-9]+)<\/TD><\/TR>/gi) {
	$name = $1;
	$tech = $TechLevels{lc($2)};
	$reliability=$3;
	$yield = $4;
	message("Module $name $tech $reliability" . "% $yield");
	mydo("insert into modules values(default, ?, ?, ?, ?, ?, ?, ?);",
	     $data->{turn}, $donor->{donorid}, $name, GetShopItemType($name),
	     $tech, $yield, $reliability);
    }

    # Artifact information

    # bless/curse regexp
    $bcre = "(?:Wd)|(?:Id)|(?:Sn)|(?:Cl)|(?:Ls)|(?:Sb)|(?:Sh)|(?:Wp)";

    while ($content =~ /<TR ALIGN=CENTER><TD>(.*?)\s*<\/TD><TD>($bcre)<\/TD><TD>((?:None)|(?:(?:$bcre)+))<\/TD><TD>([0-8]+)<\/TD>/gi) {
	$name = $1;
	$bless = $2;
	$curses = $3;
	$keys = $4;
	message("Artifact $name $bless $curses $keys");
	mydo("insert into artifacts values(default, ?, ?, ?, ?);",
	     $donor->{donorid}, $data->{turn}, $name, $bless);
	$artifactid = GetSequence('artifacts_artifactid');
	for ($i = 0; $i < length($keys); $i++) {
	    mydo("insert into keys values(?, ?);", 
		 $artifactid, substr($keys, $i, 1));
	}
	if ($curses ne "None") {
	    for ($i = 0; $i < length($curses); $i+=2) {
		mydo("insert into curses values(?, ?);",
		     $artifactid, substr($curses, $i, 2));
	    }
	}
    }

    # Medicine information

    if ($content =~ /Holding (.*) Medicine Value \$([0-9]+)/) {
	$race = $1;
	$value = $2;
	mydo("insert into medicine values (?, ?, ?, ?);",
	     $ship, $data->{turn}, 
	     SelectOne("select system from aliens where race=?;", $race),
	     $value);
    }
}

sub HandleShops {
    my($data) = @_;
    my($fh, $line);
    message("In HandleShops");
    $fh = $data->{fh};
    for (;;) {
#	message("In inner loop of HandleShops");#!!!
	if ($data->{is_terminal_report} || $data->{is_pres_report}) {
	    $line = getline($fh, undef);
#	    message("In report, line='$line'");#!!!
	    if (!defined($line)) {
		return 1;
	    }
	    $line = trim($line);
	    if ($line =~ m|^<A NAME=\"([^\"]+)\"></A><H1>Sector.*Star system (.*) \(.*\).*:<\/H1>$|) {
		ungetline($line);
		return 0;
	    }
	} elsif ($data->{is_probe_report} || $data->{is_trace_report}) {
	    $line = trim(getline($fh));
	    if ($line =~ /<HR>/) {
		ungetline($line);
		return 0;
	    }
	} else {
	    $line = trim(getline($fh));
	    if ($line eq '<H3>Religious <A HREF="http://tbg.fyndo.com/tbg/Rules.html#Favour">Favour</A></H3>') {
		message("Returning from HandleShop");
		return 0;
	    }
	}
	if ($line =~ m|^<TR><TH COLSPAN=4 ALIGN=CENTER>$data->{system} Shop-|) {
	    HandleShopDetail($data);
	}
    }
}

sub HandleShopDetail {
    my($data) = @_;
    my($fh, $line, $item, $tech, $reliability, $yield, $capacity, $donor);
    $donor = $data->{donor};
    $fh = $data->{fh};
    for (;;) {
	$line = trim(getline($fh));
	if ($line eq '</TABLE>') {
	    return;
	}
	# According to SST: In memory of the passing of Arthur C. Clarke, all sufficiently advanced technology has been dimmed galaxy wide. Requiescat in pace.
	# It appears magic modules have <FONT COLOR="#808000">Magic</FONT> around them.
	# 03/20/08

	$line =~ s|<FONT COLOR=\"\#808000\">Magic</FONT>|Magic|g;

	if ($line =~ m|^<TR ALIGN=CENTER><TD>(.*?)\s*</TD><TD>($TechRE)</TD><TD>([0-9]+)%</TD><TD>([0-9]+)</TD></TR>$|i) {
	    $item = $1;
	    $tech = $TechLevels{lc($2)};
	    $reliability = $3;
	    $yield = $4;
	    UpdateShopData($data->{system}, $data->{turn}, $donor->{donorid}, $item, 
			   $tech, $yield, $reliability, undef, $donor->{pub_shop_newbie});
	} elsif ($line =~ m|^<TR ALIGN=CENTER><TD>(.*?)\s*</TD><TD>([0-9]+)</TD><TD>Empty</TD><TD>0</TD></TR>|) {
	    $item = $1;
	    $capacity = $2;
	    UpdateShopData($data->{system}, $data->{turn}, $donor->{donorid}, $item,
			   $capacity, undef, undef, undef, $donor->{pub_shop_newbie});
	} elsif ($line eq '<TR><TH>Component</TH><TH>Tech</TH><TH>Reliability</TH><TH>E Cost</TH></TR>' || $line eq '<TR><TH>Component</TH><TH>Capacity</TH><TH>Cargo</TH><TH>Amount</TH></TR>') {
	    # Nothing
	} else {
	    error("Unexpected line in shop data '$line'\n");
	}	    
    }
}  # HandleShopDetail

#
# Update shop data.
# If it already exists, make sure it's consistent.
# Entries with undef mean "don't know".
#
# Slightly buggy if two identical items exist.
#

sub UpdateShopData {
    my($system, $turn, $donorid, $item, $tech, $yield, $reliability, $price, $sharenewbie) = @_;
    my($sth, $gotone, $row, $type);
    $gotone = 0;
    $sth = mydo("select * from shop where system=? and turn=? and item=?;",
		$system, $turn, $item);
    while ($row = $sth->fetchrow_hashref()) {
	$gotone = 1;
	message("shop item $item exists. Updating.");
	UpdateShopComponent($row, "reliability", $reliability);
	UpdateShopComponent($row, "yield", $yield);
	UpdateShopComponent($row, "price", $price);
	if ($sharenewbie) {
	    mydo("update shop set sharenewbie=true where shopid=?;", $row->{shopid});
	}
    }
    $sth->finish();
    if (!$gotone) {
	$type = GetShopItemType($item);
	message("insert shop data for $system, $item type=$type tech=$tech");
	$sth = mydo("insert into shop values(default, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
		    $system, $turn, $donorid, $item, $type, $tech, 
		    $yield, $reliability, $price, $sharenewbie);
	$sth->finish();
    }
}
		
sub UpdateShopComponent {
    my($row, $item, $value) = @_;
    my($sth);
    if (defined($value)) {
	if (defined($row->{$item})) {
	    if ($value != $row->{$item}) {
		error("Mismatched $item!");
	    }
	} else {
	    message("Updating shop data id=" . $row->{shopid} . " $item to $value");
	    $sth = mydo("update shop set $item=? where shopid=?;", $value, $row->{shopid});
	    $sth->finish();
	}
    }
}

# For now, just ignore everything except option to buy.
# Exit when you hit Mercs.
# If we appear to be in a share_SecretURL file, just return
# since there are no orders.

sub HandleOrders {
    my($data) = @_;
    if ($data->{donor}{secreturl} =~ m|^http://tbg.fyndo.com/tbg/share_[A-Z][a-z]*.htm$|) {
	return;
    }
    my($fh, $line, $tech, $item, $reliability, $price, $donor, $system);
    $fh = $data->{fh};
    $donor = $data->{donor};
    for (;;) {
	$line = trim(getline($fh));
	if ($line =~ m|<H2><A HREF=\"http://tbg.fyndo.com/tbg/Rules.html\#Mercenaries\">Mercenary</A> Actions</H2>|) {
	    return;
	}
	if ($line =~ /^<OPTION VALUE=.*>Buy ($TechRE) (.*?)\s*\(([0-9]+)%\) for \$([0-9]+)$/i) {
	    $tech = $TechLevels{lc($1)};
	    $item = $2;
	    $reliability = $3;
	    $price = $4;
	    UpdateShopData($data->{system}, $data->{turn}, $donor->{donorid}, 
			   $item, $tech, undef, $reliability, $price, $donor->{pub_shop_newbie});
	} elsif ($line =~ /^<OPTION VALUE=.*>Probe Report from (.*) \([0-9]+\)$/) {
	    $system = $1;
	    if (!ExistsSelect("select * from probes where donorid=?;", $donor->{donorid})) {
		mydo("insert into probes values(?);", $donor->{donorid});
	    }
	    mydo("update probes set system=? where donorid=?;", $system, $donor->{donorid});
	}
    }
}

# Update from President's database.
# Note that the format changes each time the pres changes.
# This one was for Annushka Moya's reports.
#
# This has been moved to updatepres.pl

sub UpdatePresAnnushkaMoya {
    my(%donor, $url, $content, $fh, $line, $header);
    my($inTradeData, $inRogueData, $price, $price2, $system, $resource);

    $url = 'http://www.tmk.com/~ben/TBG/pfoio.html';
    # Dummy donnor
    $donor{donorid} = -1;

    message("\nUpdating turn $Turn for Presidential Database");
    if (ExistsTurnUpdate(\%donor, $Turn)) {
	message("Presidential Database for turn $Turn already exists. Skipping.");
	return;
    }
    message("Turn $Turn for Presidential database does not exist. Fetching.");
    $content = GetPresPageAnnushkaMoya($url);
    if (!defined($content)) {
	warning("Failed to retrieve Presidential page");
	return;
    }
    
    if (ExistsTurnUpdate(\%donor, $Turn)) {
	warning(" Turn $Turn for Presidential Database already exists. Skipping.");
	return;
    }

    UpdateTurnUpdate(\%donor, $Turn);

    $fh = new IO::Scalar \$content;

    $inTradeData = 0;
    $inRogueData = 0;
    while ($line = <$fh>) {
	if ($line =~ /^<h3>(.*)<\/h3>$/) {
	    $header = $1;
	    if ($header eq "Trade Data") {
		$inTradeData = 1;
		$inRogueData = 0;
		next;
	    } elsif ($header eq "Rogue Bands") {
		$inTradeData = 0;
		$inRogueData = 1;		
	    } else {
		$inTradeData = 0;
		$inRogueData = 0;
		next;
	    }
	}
	if ($inTradeData) {
	
	    if ($line =~ /^\s*<td valign=\"top\">\s*(.*)\s*<\/td>\s*$/) {
		$system = $1;
		message(" Presidential Database at $system");
	    } elsif ($line =~ /^\s*(.*?)\s*-\s*([0-9]+)(,\s*([0-9]+))?\s*<br>\s*$/) {
		if (!defined($system)) {
		    error(" System not defined while parsing Presidential Database");
		    return;
		}
		$resource = $1;
		$price = $2;
		$price2 = $4;
		if (!SystemBuysResource($system, $resource)) {
		    error("Presidential Database appears to be cheating. $system does not buy $resource.");
		    return;
		}
		if (ExistsTradePrice($system, $resource, $price, $Turn, -1)) {
		    message("$resource for \$$price (confirmed)");
		} else {
		    mydo("insert into trade values(default, ?, ?, ?, ?, ?);",
			 $system, $resource, $price, $Turn, -1);
		    message("$resource for \$$price (entered)");
		}
		if (defined($price2)) {
		    if (ExistsTradePrice($system, $resource, $price2, $Turn, -1)) {
			message("$resource for \$$price2 (confirmed)");
		    } else {
			mydo("insert into trade values(default, ?, ?, ?, ?, ?);",
			     $system, $resource, $price2, $Turn, -1);
			message("$resource for \$$price2 (entered)");
		    }
		}
	    }
	} elsif ($inRogueData) {
	    if ($line =~ m|<td valign="top">(.*)</td>|) {
		$system = $1;
	    } elsif ($line =~ m|([a-z]+) ([a-z]+) in Gas Giant \(([0-9]+)%\)<br>|i) {
		AddRogueBand($system, $1, $2, 'Impulse', $3, $Turn);
	    } elsif ($line =~ m|([a-z]+) ([a-z]+) in Badland \(([0-9]+)%\)<br>|i) {
		AddRogueBand($system, $1, $2, 'Life Support', $3, $Turn);
	    }
	}
    }
} # UpdatePres

# Store Presidential page in cache.
# 
# Moved to updatepres.pl

sub GetPresPageAnnushkaMoya {
    my($url) = @_;
    my($fname, $content, $turn);
    $fname = "$Top/turns/$Turn/pres.html";
    if (!-e "$Top/turns/$Turn") {
	message("Making turn cache directory $Top/turns/$Turn");
	mkdir("$Top/turns/$Turn");
    }
    if (! -r $fname) {
	if ($CacheOnly) {
	    warning("Currently, only use cache for pres database"); #!!!
	    return undef;
	}
	message("Downloading Presidential Database from $url");
	if (!mygetstore($url, $fname)) {
	    error("Unable to getstore $url for Presidential Database");
	}
    } else {
	message("Retrieving Presidential Database from turn cache");
    }
    $content = myget("file:$fname");
    if (!defined($content)) {
	error("Couldn't retrieve turn $Turn from cache for Presidential Database at $url");
    }
    if ($content =~ /<h2>Report for turn (.*)<\/h2>/) {
	$turn = $1;
	if ($turn != $Turn) {
	    warning("Expected turn $Turn for Presidential database. Got turn $turn.\n");
	    unlink($fname);
	    return undef;
	}
    }
    return $content;
} # GetPresPageAnnushkaMoya()

# Update from President's database.
# Note that the format changes each time the pres changes.
# This one was for Gate of Truth's reports.
#
# Moved to updatepres.pl

sub UpdatePresGateOfTruth {
    my(%donor, $url, $content, $fh, $line, $header);
    my($inTradeData, $inRogueData, $price, $price2, $system, $resource);

    $url = 'http://www.wolfandweasel.com/tbg/pfoio.htm';
    # Dummy donnor
    $donor{donorid} = -1;

    message("\nUpdating turn $Turn for Presidential Database");
    if (ExistsTurnUpdate(\%donor, $Turn)) {
	message("Presidential Database for turn $Turn already exists. Skipping.");
	return;
    }
    message("Turn $Turn for Presidential database does not exist. Fetching.");
    $content = GetPresPageGateOfTruth($url);
    if (!defined($content)) {
	warning("Failed to retrieve Presidential page");
	return;
    }
    
    if (ExistsTurnUpdate(\%donor, $Turn)) {
	warning(" Turn $Turn for Presidential Database already exists. Skipping.");
	return;
    }

    UpdateTurnUpdate(\%donor, $Turn);

    $fh = new IO::Scalar \$content;

    $inTradeData = 0;
    $inRogueData = 0;
    while ($line = <$fh>) {
	$line =~ s/\r\n//;
	if ($line =~ /^<h3>(.*)<\/h3>$/) {
	    $header = $1;
	    if ($header eq "Trade Data by System") {
		$inTradeData = 1;
		$inRogueData = 0;
		next;
	    } elsif ($header eq "Rogue Bands") {
		$inTradeData = 0;
		$inRogueData = 1;		
	    } else {
		$inTradeData = 0;
		$inRogueData = 0;
		next;
	    }
	}
	if ($inTradeData) {
	    if ($line =~ /^\s*<td valign=\"top\">\s*(.*)\s*<\/td>\s*$/) {
		$system = $1;
		message(" Presidential Database at $system");
	    } elsif ($line =~ /^\s*(.*?)\s*-\s*([0-9]+)(,\s*([0-9]+))?\s*<br>\s*$/) {
		if (!defined($system)) {
		    error(" System not defined while parsing Presidential Database");
		    return;
		}
		$resource = $1;
		$price = $2;
		$price2 = $4;
		if (!SystemBuysResource($system, $resource)) {
		    error("Presidential Database appears to be cheating. $system does not buy $resource.");
		    return;
		}
		if (ExistsTradePrice($system, $resource, $price, $Turn, -1)) {
		    message("$resource for \$$price (confirmed)");
		} else {
		    mydo("insert into trade values(default, ?, ?, ?, ?, ?);",
			 $system, $resource, $price, $Turn, -1);
		    message("$resource for \$$price (entered)");
		}
		if (defined($price2)) {
		    if (ExistsTradePrice($system, $resource, $price2, $Turn, -1)) {
			message("$resource for \$$price2 (confirmed)");
		    } else {
			mydo("insert into trade values(default, ?, ?, ?, ?, ?);",
			     $system, $resource, $price2, $Turn, -1);
			message("$resource for \$$price2 (entered)");
		    }
		}
	    }
	} elsif ($inRogueData) {
	    if ($line =~ m|<td valign="top">(.*)</td>|) {
		$system = $1;
	    } elsif ($line =~ m|([a-z]+) ([a-z]+) in Gas Giant \(([0-9]+)%\)<br>|i) {
		AddRogueBand($system, $1, $2, 'Impulse', $3, $Turn);
	    } elsif ($line =~ m|([a-z]+) ([a-z]+) in Badland \(([0-9]+)%\)<br>|i) {
		AddRogueBand($system, $1, $2, 'Life Support', $3, $Turn);
	    }
	}
    }
} # UpdatePresGateOfTruth()

# Store Presidential page in cache.
#
# Moved to updatepres.pl

sub GetPresPageGateOfTruth {
    my($url) = @_;
    my($fname, $content, $turn);
    $fname = "$Top/turns/$Turn/pres.html";
    if (!-e "$Top/turns/$Turn") {
	message("Making turn cache directory $Top/turns/$Turn");
	mkdir("$Top/turns/$Turn");
    }
    if (! -r $fname) {
	if ($CacheOnly) {
	    warning("Currently, only use cache for pres database"); #!!!
	    return undef;
	}
	message("Downloading Presidential Database from $url");
	if (!mygetstore($url, $fname)) {
	    error("Unable to getstore $url for Presidential Database");
	}
    } else {
	message("Retrieving Presidential Database from turn cache");
    }
    $content = myget("file:$fname");
    if (!defined($content)) {
	error("Couldn't retrieve turn $Turn from cache for Presidential Database at $url");
    }
    if ($content =~ /<h2>Report for turn (.*)<\/h2>/) {
	$turn = $1;
	if ($turn != $Turn) {
	    warning("Expected turn $Turn for Presidential database. Got turn $turn.\n");
	    unlink($fname);
	    return undef;
	}
    }
    return $content;
} # GetPresPageGateOfTruth()

sub AddRogueBand {
    my($system, $race, $field, $location, $danger, $turn) = @_;
    if (ExistsSelect("select race from rogues where race=? and field=? and location=? and danger=? and system=? and turn=?;",
		     $race, $field, $location, $danger, $system, $turn)) {
	message("$race Rogue band (confirmed)");
    } else {
	mydo("insert into rogues values(?, ?, ?, ?, ?, ?);",
	     $race, $field, $location, $danger, $system, $turn);
	message("$race Rogue band (inserted)");
    }
}

#
# If the turn update for the given donor and turn have already
# been entered, return true. Otherwise, return 0.
#

sub ExistsTurnUpdate {
    my($donor, $turn) = @_;
    my($sth, $row);

    $sth = mydo("select turn from turnupdate where donorid=? and turn=?;", $donor->{donorid}, $turn);
    $row = $sth->fetchrow_hashref();
    $sth->finish();
    if (defined($row) && exists($row->{turn}) && $row->{turn} == $turn) {
	return 1;
    } else {
	return 0;
    }
} # ExistsTurnUpdate

# 
# Given a donor and a turn, create a turnupdate if it doesn't exist.
#

sub UpdateTurnUpdate {
    my($donor, $turn) = @_;
    my($sth, $row, $id, $dturn);

    if (!ExistsTurnUpdate($donor, $turn)) {
	mydo("insert into turnupdate values(?, ?);", $turn, $donor->{donorid});
    }
}

#
# Load some static data such as which system buys which resource
#

sub LoadStaticData {
    %TechLevels = qw(primitive 1 basic 2 mediocre 3 advanced 4 exotic 5 magic 6);
    $TechRE = join('|', keys(%TechLevels));
    %SystemBuys = ('alphard' => {'eyerobots' => 1, 'sharpsticks' => 1, 'newtricks' => 1},
'rastaban' => {'ray-guns' => 1, 'emperorsnewclothes' => 1, 'dilithium' => 1, 'winegums' => 1, 'lists' => 1, 'emperorsnewclothes' => 1},
'canopus' => {'tea' => 1, 'steelyknives' => 1, 'oldsongs' => 1, 'tea' => 1, 'scrap' => 1},
'procyon' => {'webpages' => 1, 'snowmen' => 1},
'vega' => {'elvismemorabilia' => 1, 'oldsongs' => 1, 'ray-guns' => 1},
'castor' => {'steelyknives' => 1, 'emperorsnewclothes' => 1, 'emperorsnewclothes' => 1, 'quadtrees' => 1, 'mittens' => 1, 'elvismemorabilia' => 1},
'lupi' => {'fudge' => 1, 'winegums' => 1, 'beards' => 1, 'ninjabeer' => 1, 'sharpsticks' => 1},
'achernar' => {'boardgames' => 1, 'steelyknives' => 1, 'beards' => 1},
'bootis' => {'snowmen' => 1, 'hats' => 1},
'cephei' => {'euphoria' => 1, 'puddings' => 1, 'webpages' => 1, 'surprises' => 1, 'steelyknives' => 1, 'lists' => 1, 'oldsongs' => 1},
'eridani' => {'windows' => 1, 'oldsongs' => 1},
'altair' => {'videos' => 1, 'elvismemorabilia' => 1, 'hats' => 1, 'tea' => 1},
'regulus' => {'xylophones' => 1, 'ray-guns' => 1, 'scrap' => 1, 'dilithium' => 1, 'hankies' => 1, 'mittens' => 1},
'hydrae' => {'emperorsnewclothes' => 1, 'steelyknives' => 1, 'hats' => 1, 'dilithium' => 1, 'oldsongs' => 1, 'sharpsticks' => 1},
'pherda' => {'hankies' => 1, 'ray-guns' => 1, 'ray-guns' => 1, 'mittens' => 1, 'dilithium' => 1},
'betelgeuse' => {'elvismemorabilia' => 1, 'xylophones' => 1, 'chocolate' => 1},
'hamal' => {'euphoria' => 1, 'ninjabeer' => 1, 'puddings' => 1, 'tea' => 1},
'capella' => {'mittens' => 1, 'puddings' => 1, 'surprises' => 1},
'markab' => {'hankies' => 1, 'quadtrees' => 1, 'scrap' => 1, 'chocolate' => 1},
'sirius' => {'chocolate' => 1, 'lists' => 1, 'steelyknives' => 1, 'jumpers' => 1},
'wolf' => {'euphoria' => 1, 'scrap' => 1, 'fudge' => 1, 'eyerobots' => 1},
'adhara' => {'hankies' => 1, 'surprises' => 1, 'xylophones' => 1, 'elvismemorabilia' => 1},
'mirfak' => {'newtricks' => 1, 'euphoria' => 1},
'pollux' => {'chocolate' => 1, 'xylophones' => 1, 'windows' => 1, 'eyerobots' => 1},
'mizar' => {'jumpers' => 1, 'elvismemorabilia' => 1, 'fudge' => 1},
'alnitak' => {'fudge' => 1},
'rigel' => {'tea' => 1, 'marzipan' => 1},
'diphda' => {'windows' => 1, 'oldsongs' => 1, 'eyerobots' => 1, 'xylophones' => 1, 'windows' => 1, 'sharpsticks' => 1, 'emperorsnewclothes' => 1},
'thuban' => {'tea' => 1, 'eyerobots' => 1},
'arcturus' => {'boardgames' => 1, 'marzipan' => 1},
'alcor' => {'webpages' => 1, 'xylophones' => 1, 'elvismemorabilia' => 1, 'fudge' => 1},
'mira' => {'marzipan' => 1},
'caph' => {'puddings' => 1, 'videos' => 1, 'emperorsnewclothes' => 1, 'marzipan' => 1},
'sadir' => {'euphoria' => 1, 'scrap' => 1, 'snowmen' => 1, 'winegums' => 1, 'fudge' => 1, 'quadtrees' => 1, 'scrap' => 1},
'algol' => {'marzipan' => 1, 'eyerobots' => 1, 'webpages' => 1},
'tauri' => {'eyerobots' => 1, 'winegums' => 1, 'hats' => 1, 'euphoria' => 1, 'surprises' => 1},
'olympus' => {'eyerobots' => 1, 'sharpsticks' => 1, 'beards' => 1, 'puddings' => 1, 'scrap' => 1, 'marzipan' => 1, 'webpages' => 1, 'xylophones' => 1, 'quadtrees' => 1, 'dilithium' => 1, 'lists' => 1, 'winegums' => 1, 'hankies' => 1, 'windows' => 1, 'surprises' => 1, 'ray-guns' => 1, 'fudge' => 1, 'oldsongs' => 1},
'kochab' => {'beards' => 1, 'hats' => 1, 'ninjabeer' => 1, 'elvismemorabilia' => 1},
'merak' => {'mittens' => 1, 'euphoria' => 1, 'hankies' => 1},
'schedar' => {'snowmen' => 1, 'snowmen' => 1, 'lists' => 1},
'kapetyn' => {'webpages' => 1, 'emperorsnewclothes' => 1},
'fomalhaut' => {'tea' => 1, 'surprises' => 1, 'windows' => 1},
'scorpii' => {'hats' => 1, 'ninjabeer' => 1, 'ray-guns' => 1, 'snowmen' => 1, 'boardgames' => 1},
'indi' => {'newtricks' => 1, 'mittens' => 1, 'webpages' => 1, 'newtricks' => 1, 'quadtrees' => 1, 'jumpers' => 1, 'videos' => 1},
'lyrae' => {'quadtrees' => 1, 'ninjabeer' => 1, 'sharpsticks' => 1, 'marzipan' => 1, 'videos' => 1, 'oldsongs' => 1, 'videos' => 1},
'antares' => {'boardgames' => 1, 'beards' => 1, 'winegums' => 1, 'beards' => 1, 'quadtrees' => 1, 'lists' => 1, 'quadtrees' => 1, 'marzipan' => 1, 'puddings' => 1},
'deneb' => {'dilithium' => 1, 'hankies' => 1, 'tea' => 1, 'beards' => 1, 'windows' => 1},
'zosca' => {'dilithium' => 1, 'snowmen' => 1, 'sharpsticks' => 1, 'dilithium' => 1, 'newtricks' => 1, 'webpages' => 1},
'spica' => {'windows' => 1, 'steelyknives' => 1},
'canis' => {'ray-guns' => 1, 'winegums' => 1, 'winegums' => 1},
'aldebaran' => {'hats' => 1, 'boardgames' => 1, 'puddings' => 1, 'lists' => 1, 'mittens' => 1, 'boardgames' => 1, 'ninjabeer' => 1},
'ophiuchi' => {'lists' => 1, 'videos' => 1, 'jumpers' => 1},
'kruger' => {'chocolate' => 1, 'euphoria' => 1, 'jumpers' => 1},
'aurigae' => {'hankies' => 1, 'mittens' => 1, 'beards' => 1, 'ninjabeer' => 1, 'chocolate' => 1, 'videos' => 1},
'alioth' => {'videos' => 1, 'jumpers' => 1, 'snowmen' => 1, 'scrap' => 1, 'boardgames' => 1},
'ceti' => {'ninjabeer' => 1, 'surprises' => 1},
'ross' => {'newtricks' => 1, 'puddings' => 1},
'polaris' => {'newtricks' => 1, 'jumpers' => 1},
'cygni' => {'steelyknives' => 1, 'fudge' => 1, 'sharpsticks' => 1, 'chocolate' => 1},
'centauri' => {'surprises' => 1, 'xylophones' => 1, 'jumpers' => 1, 'chocolate' => 1},
'wezen' => {'newtricks' => 1, 'hats' => 1, 'boardgames' => 1},
		   );
} # LoadStaticData

#
# Return 1 if the given system does, in fact, buy the given resource.
# Return 0 otherwise
# 

sub SystemBuysResource {
    my($s, $r) = @_;
    $s = normalize_starname($s);
    $r = normalize_resname($r);
    if (!exists($SystemBuys{$s}) || !exists($SystemBuys{$s}->{$r})) {
	return 0;
    } else {
	return 1;
    }
} # SystemBuysResource

sub normalize_starname {
    my($star) = @_;
    $star = lc($star);
    $star =~ s/\s+//g;
    $star =~ s/^star/s/;
    $star =~ s/^s\#/s/;
    return $star;
}

sub normalize_resname {
    my($res) = @_;
    $res = lc($res);
    $res =~ s/\s+//g;
    $res =~ s/\(\!\)$//;
    $res =~ s/\'//g;
    return $res;
}

# Update who may be chased by Dybuk this turn.
# It only scans my turn page, since they should all be the same.
# 
# Since I quit the game, this will not work! Woops. It'll probably never
# be implemented anyway, so I've just removed the call to UpdateDybuk.

sub UpdateDybuk {
    my($fh, $line, $ship, $id);

    message("Updating Dybuk entries.");
    $fh = new FileHandle("$Top/turns/$Turn/1.html") or die "Couldn't open turn for updating Dybuk";
    while ($line = <$fh>) {
	if ($line =~ /<select name=P>/) {
	    while ($line && $line !~ /<\/select>/) {
		if ($line =~ /<option value=d([0-9]+)>(.*)\s*$/) {
		    $id = $1;
		    $ship = $2;
		    if ($id != 0 && !ExistsSelect("select * from dybuk where turn=? and ship=?", $Turn, $ship)) {
			mydo("insert into dybuk values(?, ?);", $Turn, $ship);
		    }
		}
		$line = <$fh>;	
	    }
	    last;
	}
    }
    $fh->close();
}

# Update the "active" e.g. non-retired list

sub UpdateActive {
    my($content, $list, $id, $ship);
    $content = myget("http://tbg.fyndo.com/tbg/alias.html");
    if ($content =~ m|<SELECT NAME=\"t\">\s+<OPTION VALUE=0>CHANGE THIS TO SOMETHING ELSE!\s*(.*?)\s*</SELECT>|s) {
	$list = $1;
	while ($list =~ /<OPTION VALUE=([0-9]+)>(.*)/g) {
	    $id = $1;
	    $ship = $2;
	    if (!ExistsSelect("select * from activeships where turn=? and ship=?;", $Turn, $ship)) {
		mydo("insert into activeships values(?, ?, ?);",
		     $Turn, $ship, $id);
	    }
	}
    } else {
	print STDERR "Failed to match active.\n";
    }
}


# By default, error if EOF.
# If arg is provided, return it instead of signaling an error.

sub getline {
    my($faileof, $sigeof, $fh, $ret);
    if ($#_ == 0) {
	$faileof = 1;
    } elsif ($#_ == 1) {
	$faileof = 0;
	$sigeof = $_[1];
    } else {
	error("getline called with wrong number of args");
    }	
    $fh = $_[0];
    if ($#UngetLines >= 0) {
	return pop(@UngetLines);
    }
    $ret = <$fh>;
    if (!defined($ret)) {
	if ($faileof) {
	    error("Unexpected end of file");
	} else {
	    return $sigeof;
	}
    }
    return $ret;
}

sub ungetline {
    my($line) = @_;
    push(@UngetLines, $line);
}

sub usage {
    print STDERR "Usage: update.pl -h -t turn\n";
    print STDERR "\t-h      This message\n";
    print STDERR "\t-t turn Update this turn (otherwise, pick max)\n\n";
    exit;
}

sub message {
    my $str = join(' ', @_);
    print $MessageFH "$str\n";
}

sub warning {
    my $str = join(' ', @_);
    print $MessageFH "$str\n";
    print $WarningFH "$str\n";
    print STDERR "$str\n";
}

sub error {
    my $str = join(' ', @_);
    print $MessageFH "ERROR: $str\n";
    print $WarningFH "ERROR: $str\n";
    print STDERR "ERROR: $str\n";
    exit;
}

# Get the given URL.
# Tries three times.
# On success, return the contents.
# On failure, returns undef.

sub myget {
    my($url) = @_;
    my($content, $try);
    for ($try = 0; $try < 3; $try++) {
	$content = get($url);
	if (!defined($content)) {
	    warning("myget($url) failed, try $try");
	} else {
	    return $content;
	}
    }
    warning("myget($url) failed too many times. Giving up.");
    return undef;
}

# Get the URL and store it in fname.
# Try 3 times. If all three fail, return 0.
# Return 1 on success.

sub mygetstore {
    my($url, $fname) = @_;
    my($try);
    for ($try = 0; $try < 3; $try++) {
    	if (!is_success(getstore($url, $fname))) {
	    warning("mygetstore($url, $fname) failed, try $try");
	} else {
	    return 1;
	}
    }
    warning("mygetstore($url, $fname) failed too many times. Giving up.");
    return 0;
}

