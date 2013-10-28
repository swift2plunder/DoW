#!/usr/bin/perl -w
#
# Given downloaded data for a turn, update the database.
#
# Note that DOW scripts are generally unavailable during
# update.
#
# Loosely a recursive descent parser, but extremely ad-hoc. I really
# wish I could think of a better way of doing this.
#
# Latest attempt:
#   Load all data from the database into local hashes. The only other
#   interaction with the database is to insert new data. The 'shared'
#   table is by far the largest, since it records who can see which
#   individual piece of data. It is updated by writing the updates
#   to a file, and updating the database in one go from post_turn().
#

use strict;
use Getopt::Std;

use dow2;

# Command line options

use vars qw($opt_t);

# Globals
my @OrigARGV = @ARGV;
my $ArchivePath;	# Where to store stuff
my @UngetLines;		# Used with getline/ungetline

my %ShipIIDs;		# Map of ship to list ref of IIDs of data for shipconfigs.
			# Set while reading ships; used while updating sharing settings.

my @ShipConfigTables;	# The tables that are controlled by the shipconfig sharing type.
			# Set in ReadDatabaseTables().

# Updates to the "shared" table are deferred since there are a large number of
# entries, and individual updates can be slow. Instead, updates are written
# to the ascii file specified by the path below, then loaded using the
# Postgresql COPY command.

my $SharedUpdateTmpPath;
my $SharedUpdateTmpFH;

######################################################################
#
# Local copy of database entries for this turn. Note that these should
# generally start off empty, and grow as data is processed. The data
# in these globals and the database must be kept in sync (e.g. when
# data is added to a local, it should also be inserted into the DB).
#
# In most cases, the data are stored in hashes, where the key is
# some unique combination of elements and the value is a hashref
# with the columns.
#

#  Table Name          # Key
my %ShipLocTable;      # ship
my %MeetingsTable;     # ship1 (ship1 is the only one that is always provided)
my %SharedTable;       # ship:iid
my %PlaguesTable;      # system
my %TradeTable;	       # locid
my %ModulesTable;      # name
my %PodsTable;	       # name

# With whom each donor shares data from a given table.
my %SharingTable;      # sharership:table => [ shareeship1 shareeship2 ... ]	


OpenDB("dow2");

# Use the value in params.turn unless -t is specified.

$opt_t = SelectOneWithDefault("select processturn from params;", undef);

getopts('t:') or usage();

if (!defined($opt_t)) {
    error("Unable to automatically determine turn. Please use update.pl -t turn.");
}

OpenLogs("update", $opt_t);
message("\n----------\nupdate.pl called with arguments '" . join(" ", @OrigARGV) . "' on " .  `date`);

$ArchivePath = SelectOne("select topdir from params;") . "/" . SelectOne("select archive from params;") . "/$opt_t";

if (! -d $ArchivePath) {
    error("Can't find path '$ArchivePath'. Perhaps you need to run start.pl and/or download.pl first?");
}

pre_turn();
update_all();
post_turn();

CloseLogs();
CloseDB();

exit;

# All subs below here.

sub pre_turn {
    $SharedUpdateTmpPath = "/tmp/sharedupdate$opt_t.tmp";
    if (-e $SharedUpdateTmpPath) {
	warning("$SharedUpdateTmpPath already exists. It will be overwritten.");
    }
    $SharedUpdateTmpFH = new FileHandle(">$SharedUpdateTmpPath") or error("Couldn't open $SharedUpdateTmpPath for writing: $!");
    ReadDatabaseTables();
}

sub post_turn {
    # Write the shared table to the database. Delete the tmp file.
    print $SharedUpdateTmpFH "\\.\n";
    $SharedUpdateTmpFH->close();

    # It's faster to drop the indices, copy, then recreate the indices. This may
    # change as more turns are entered.
    message("Copying shared table to database.");
    mydo("DROP INDEX shared_index1; DROP INDEX shared_index2; DROP INDEX shared_index3; COPY shared (ship, iid, turn) FROM '$SharedUpdateTmpPath'; CREATE INDEX shared_index1 ON shared (iid); CREATE INDEX shared_index2 ON shared (ship); CREATE INDEX shared_index3 ON shared (turn);");
    message(" Done copying data.");
    unlink($SharedUpdateTmpPath);
}

sub update_all {
    my($sth, $row);

    # We first have to update ships so the information is present when
    # we update players.

    $sth = mydo("select * from downloadfiles where turn=$opt_t and status='Traversed' and type='Ship' order by failures;");
    while ($row = $sth->fetchrow_hashref()) {
	update_ship($row);
	mydo("update downloadfiles set status='Done' where id=?;", $row->{id});
    }
    $sth->finish();

    $sth = mydo("select * from downloadfiles where turn=$opt_t and status='Traversed' order by failures;");
    while ($row = $sth->fetchrow_hashref()) {
	if ($row->{type} eq 'Alias File') {
	    update_alias_file($row);
	} elsif ($row->{type} eq 'SST') {
	    update_sst($row);
	} elsif ($row->{type} eq 'Ship') {
	    error("Failed to update ship $row->{name}. This should never happen!");
	} elsif ($row->{type} eq 'Terminal Report') {
	    update_terminal_report($row);
	} elsif ($row->{type} eq 'Presidential Report') {
	    update_presidential_report($row);
	} elsif ($row->{type} eq 'Player') {
	    update_player($row);
	} else {
	    error("Unexpected download file type '$row->{type}'. This shouldn't happen!");
	}
	# if we reached here, then the update should have been successful.
	mydo("update downloadfiles set status='Done' where id=?;", $row->{id});
    }
    $sth->finish();
}  # update_all()

######################################################################
#
# Reads the alias file (typically from the TBG server) and updates
# the activeships tables.
#

sub update_alias_file {
    my($dlfile) = @_;
    my($fh, $line, $id, $ship);
    message("\nUpdating alias file");
    $fh = new FileHandle("$ArchivePath/$dlfile->{filename}");
    clearungetlines();
    if (!defined($fh)) {
	error("Couldn't read alias file $dlfile->{filename}: $!");
    }
    while ($line = getline($fh)) {
	chop($line);
	last if ($line eq '<OPTION VALUE=0>CHANGE THIS TO SOMETHING ELSE!');
    }
    while ($line = getline($fh)) {
	chop($line);
	last if $line eq '</SELECT>';
	if ($line =~ m|^<OPTION VALUE=([0-9]+)>(.*?)$|) {
	    $id = $1;
	    $ship = $2;
	    mydo("insert into activeships (turn, ship, id) values (?, ?, ?);",
		 $opt_t, $ship, $id);
	} else {
	    error("Parse of alias file failed on '$line'");
	}
    }
    if ($line ne '</SELECT>') {
	error("Failed to find end of list in alias file (found '$line' instead).");
    }
    $fh->close();
} # update_alias_file()

######################################################################
#
# Read the Subspace Times (typically from the TBG server) and
# update offices table.
#
# NOTE: Not yet implemented!
#

sub update_sst {
    my($dlfile) = @_;
} # update_sst()

######################################################################
#
# Update a ship from a ship page. Does NOT update sharing, since
# that's done from update_player.
#

sub update_ship {
    my($dlfile) = @_;
    my($fh, $line, $nextline, $flag, $ship);
    my($name, $tech, $reliability, $yield, $techre, $broken);
    my($capacity, $resource, $carrying, $bcre);
    my($i, $bless, $curses, $keys, $artifactid);
    my($race, $value, $mass, $torpedos);
    my($warp, $impulse, $sensor, $cloak, $lifesupport, $sickbay, $shield, $weapon);
    my($combatmass, $powerrank, $techlevel);

    $ship = $dlfile->{name};

    message("\nupdate_ship $ship");

    $combatmass = 0;	# Mass excluding artifacts
    $powerrank = 0;

    $techre = TechRE();

    # bless/curse regexp
    $bcre = "(?:Wd)|(?:Id)|(?:Sn)|(?:Cl)|(?:Ls)|(?:Sb)|(?:Sh)|(?:Wp)";


    $fh = new FileHandle("$ArchivePath/$dlfile->{filename}") or error("Couldn't open ship file '$dlfile->{filename}': $!");
    clearungetlines();
    $line = getline($fh);
    if ($line ne "<HTML><HEAD><TITLE>$ship, Turn $opt_t</TITLE></HEAD>\n") {
	error("Ship $ship header failed to match");
    }

    # Extract flag from player ships. There's a formatting bug where
    # a bit of the flag sometimes appears on the next line. This makes
    # this code uglier than need be...
    if ($ship !~ /[0-9]$/) {
	while ($line = getline($fh)) {
	    if ($line =~ /^<TR><TH COLSPAN=4 ALIGN=CENTER>/) {
		$nextline = getline($fh);
		if ($nextline eq ")</TH></TR>\n") {
		    $line .= $nextline;
		} else {
		    ungetline($nextline);
		}
		if ($line =~ m|<TR><TH COLSPAN=4 ALIGN=CENTER>(.*?)</TH></TR>|s) {
		    $flag = $1;
		    $flag =~ s/\n\)/\)/g;	# Little formatting bug in page
		    mydo("insert into flags (ship, flag, turn) values (?, ?, ?);",
			 $ship, $flag, $opt_t);
		    push(@{$ShipIIDs{$ship}}, GetSequence('iid'));
		}
		last;
	    }
	}
    }

    while ($line = getline($fh)) {
	# Extract modules
	if ($line eq "<TR><TH>Component</TH><TH>Tech</TH><TH>Reliability</TH><TH>E Yield</TH></TR>\n") {
	    while ($line = getline($fh)) {
		if ($line =~ m|^<TR ALIGN=CENTER><TD>(.*?)\s*</TD><TD>($techre)</TD><TD>\s*([0-9]+)%\s*</TD><TD>([0-9]+)</TD></TR>|i) {
		    $name = $1;
		    $tech = $2;
		    $reliability=$3;
		    $yield=$4;
		    if ($name =~ /\(U\)$/) {
			$broken = 1;
			$name =~ s/\s*\(U\)$//;
		    } else {
			$broken = 0;
		    }
		    $techlevel = TechNameToLevel($tech);
		    mydo("insert into modules (iid, turn, loctype, loc, name, broken, type, tech, yield, reliability) values(default, ?, 'ship', ?, ?, ?, ?, ?, ?, ?);",
			 $opt_t, $ship, $name, $broken, ItemNameToType($name), $techlevel, $yield, $reliability);
		    push(@{$ShipIIDs{$ship}}, GetSequence('iid'));
		    $combatmass += 1;
		    # Demo and broken modules do not count for powerrank
		    if ((! $broken) && ($name !~ /D$/)) {
			$powerrank += $techlevel;
		    }
#		    message(" $ship, $name, $broken, $techlevel");
		} else {
		    ungetline($line);
		    last;
		}
	    }

	# Extract pods
	} elsif ($line eq "<TR><TH>Component</TH><TH>Capacity</TH><TH>Cargo</TH><TH>Amount</TH></TR>\n") {
	    while ($line = getline($fh)) {
		if ($line =~ m|^<TR ALIGN=CENTER><TD>(.*?)\s*</TD><TD>([0-9]+)</TD><TD>(.*?)\s*</TD><TD>([0-9]+)</TD></TR>|i) {
		    $name = $1;
		    $capacity = $2;
		    $resource = $3;
		    $carrying = $4;
##		    message(" $ship, pod $line, $name, $capacity, $resource, $carrying");
		    mydo("insert into pods (turn, loctype, loc, name, capacity, resource, carrying) values (?, 'ship', ?, ?, ?, ?, ?);", $opt_t, $ship, $name, $capacity, $resource, $carrying);
		    push(@{$ShipIIDs{$ship}}, GetSequence('iid'));
		    # Each pod counts for 1 mass (even when empty) plus the amount of
		    # cargo it is carrying.
		    $combatmass += $carrying + 1;
		    # Demo pods don't count for powerrank
		    if ($name !~ /D$/) {
			$powerrank += $capacity;
		    }
		} else {
		    ungetline($line);
		    last;
		}
	    }

        # Extract artifacts
	} elsif ($line eq "<TR><TH>Artifact</TH><TH>Bless</TH><TH>Curse</TH><TH>Keys</TH></TR>\n") {
	    while ($line = getline($fh)) {
		if ($line =~ /<TR ALIGN=CENTER><TD>(.*?)\s*<\/TD><TD>($bcre)<\/TD><TD>((?:None)|(?:(?:$bcre)+))<\/TD><TD>([0-8]+)<\/TD>/i) {
		    $name = $1;
		    $bless = $2;
		    $curses = $3;
		    $keys = $4;
#		    message(" $ship, artifact $name $bless $curses $keys");
		    mydo("insert into artifacts (turn, ship, name, bless) values (?, ?, ?, ?);",
			 $opt_t, $ship, $name, $bless);
		    push(@{$ShipIIDs{$ship}}, GetSequence('iid'));
		    $artifactid = GetSequence('artifacts_artifactid');
		    for ($i = 0; $i < length($keys); $i++) {
			mydo("insert into keys (artifactid, key) values(?, ?);", 
			     $artifactid, substr($keys, $i, 1));
		    }
		    if ($curses ne "None") {
			for ($i = 0; $i < length($curses); $i+=2) {
			    mydo("insert into curses (artifactid, curse) values(?, ?);",
				 $artifactid, substr($curses, $i, 2));
			}
		    }
		} elsif ($line eq "</TR>\n") {
		} else {
		    ungetline($line);
		    last;
		}
	    }

        # Medicine
	} elsif ($line =~ /^<P>Holding (.*?) Medicine Value \$([0-9]+)$/) {
	    $race = $1;
	    $value = $2;
	    mydo("insert into medicine (turn, ship, system, race, value) values (?, ?, ?, ?, ?);", $opt_t, $ship, SelectOne("select system from aliens where race=?;", $race), $race, $value);
	    push(@{$ShipIIDs{$ship}}, GetSequence('iid'));

	# Misc
	} elsif ($line =~ m|<P><STRONG>Mass = ([0-9]+), Energy Yield = ([0-9]+), Torpedo Stock = ([0-9]+), Cargo capacity: ([0-9]+) </STRONG><P>|) {
	    $mass = $1;
	    $yield = $2;
	    $torpedos = $3;
	    $capacity = $4;
	    mydo("insert into shipmisc (turn, ship, mass, combatmass, powerrank, yield, torpedos, cargo) values (?, ?, ?, ?, ?, ?, ?, ?);", $opt_t, $ship, $mass, $combatmass, $powerrank, $yield, $torpedos, $capacity);
	    push(@{$ShipIIDs{$ship}}, GetSequence('iid'));

	# Percentages
	} elsif ($line =~ /^Warp ([0-9]+)%, Impulse ([0-9]+)%, Sensor ([0-9]+)%, Cloak ([0-9]+)%, Life Support ([0-9]+)%, Sickbay ([0-9]+)%, Shield ([0-9]+)%, Weapon ([0-9]+)%$/) {
	    $warp = $1;
	    $impulse = $2;
	    $sensor = $3;
	    $cloak = $4;
	    $lifesupport = $5;
	    $sickbay = $6;
	    $shield = $7;
	    $weapon = $8;
	    mydo("insert into shippercents (turn, ship, warp, impulse, sensor, cloak, lifesupport, sickbay, shield, weapon) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
		 $opt_t, $ship, $warp, $impulse, $sensor, $cloak, $lifesupport, $sickbay, $shield, $weapon);
	    push(@{$ShipIIDs{$ship}}, GetSequence('iid'));
    
        # Terminate at the end
	} elsif ($line eq "</CENTER></BODY></HTML>\n") {
	    last;
	}
    }
    $fh->close();
    message(" Done updating ship.");
} # update_ship()

######################################################################
#
# Update data from a terminal report. 
#
# NOTE: Not yet implemented!
#

sub update_terminal_report {
    my($dlfile) = @_;
} # update_terminal_report()

######################################################################
#
# Update data from a presidential report.
#
# NOTE: Not yet implemented!
#

sub update_presidential_report {
    my($dlfile) = @_;
} # update_presidential_report()

######################################################################
#
# Update data from a player page, including sharing information.
#
# NOTE: Only partially implemented.
#

sub update_player {
    my($dlfile) = @_;
    my($ship, $fh, %data);
    $ship = $dlfile->{name};
    message("\nupdate_player $ship");
    $fh = new FileHandle("$ArchivePath/$dlfile->{filename}") or error("Couldn't open ship file '$dlfile->{filename}': $!");
    clearungetlines();

    $data{ship} = $ship;
    $data{fh} = $fh;

    # Each subsection should read and discard data from $fh until the
    # appropriate section is found, read and process data within the
    # section, and leave the following line in place for the next
    # subsection to process. If this isn't possible, the subsection
    # and effected other subsections should note it prominently.

    player_header(\%data);
    player_actions(\%data);
    player_skills(\%data);
    player_adventures(\%data);
    player_terminals(\%data);
    player_criminals(\%data);
    player_enemies(\%data);
    player_system(\%data);
    player_ships(\%data);
    player_shops(\%data);
#    player_favour(\%data);
#    player_politics(\%data);
#    player_finances(\%data);
#    player_commands(\%data);
    
    $fh->close();
} # update_player()


sub player_header {
  my($data) = @_;
  my($line, $pageship, $pageturn);
  while ($line = getline($data->{fh})) {
      if ($line =~ m|<H1>To Boldly Go - Starship (.*), Turn ([0-9]+)</H1>|) {
	  $pageship = $1;
	  $pageturn = $2;
	  if ($pageship ne $data->{ship} || $opt_t != $pageturn) {
	      error("Mismatch in ship name or turn. This should never happen!");
	  }
	  return;
      }
  }
  error("Failed to find header for $data->{ship}");
} # player_header()

######################################################################
#
# Not implemented, and probably never will be.
#

sub player_actions {
  my($data) = @_;
}

sub player_skills {
  my($data) = @_;
}

sub player_adventures {
  my($data) = @_;
}

sub player_terminals {
  my($data) = @_;
}

sub player_criminals {
  my($data) = @_;
}

sub player_enemies {
  my($data) = @_;
}

######################################################################
#
# Update the system report from a player page (or terminal report
# or presidential report).
#
# NOTE: Not implemented for terminal or presidential reports.
#

sub player_system {
  my($data) = @_;
  my($line, $system, $plague, $oid, $iid, $sharee);
  while ($line = getline($data->{fh})) {
      if ($line =~ m|^<A NAME=\"([^\"]+)\"></A><H1>Sector.*Star system (.*) \(.*\).*:<\/H1>$|) {
	  $system = $1;
	  if ($system ne $2) {
	      error(" Strange mismatch in system names");
	  }
	  if ($system =~ /Holiday Planet/) {
	      $system = 'Holiday Planet';
	  }
	  $data->{system} = $system;
	  if ($line =~ m|Plague at ([0-9]+)%|) {
	      $plague = $1;
	      UpdateDataAndShared($data->{ship}, \%PlaguesTable, 'plagues', $system, 
			     { turn => $opt_t, system => $system, level => $plague} );
	  }
	  message(" in system $system");
	  last;
      }
  }
  while ($line = getline($data->{fh})) {
      last if ($line eq "<H2>Locations in this system</H2>\n");
  }
  while ($line = getline($data->{fh})) {
      last if ($line eq "<TABLE BORDER=1><TR><TH>Id</TH><TH>Description</TH></TR>\n");
  }
  while ($line = getline($data->{fh})) {
      if ($line =~ m|^<TR><TD>([0-9]+)</TD><TD>(.*)$|) {
	  player_system_location($data, $1, $2);
      } elsif ($line =~ m|^\s*$|) {
	  # Nothing
      } elsif ($line eq "</TABLE>\n") {
	  last;
      } else {
	  error("Unexpected line while handling system locations $line");
      }
  }
} # player_system()

sub player_system_location {
    my($data, $locid, $desc) = @_;
    my($resource, $price, $system, $oid);

#    message(" location $locid $desc");
    # Handle colony buying stuff...
    if ($desc =~ /buying (.*?) for \$([0-9]+) /) {
	$resource = $1;
	$price = $2;
	$system = SelectOne("select system from colonies where locid=?;", $locid);

	UpdateDataAndShared($data->{ship}, \%TradeTable, 'trade', $locid, { 
	    turn => $opt_t,
	    locid => $locid,
	    system => $system,
	    resource => $resource,
	    price => $price 
	    });
    }
} # player_system_location()

######################################################################
#
# Update ship location and meetings. Also set sharing for ship
# configurations (which were already entered by update_ship()).
#
# Note the use of ' ' for entries that don't occur. This is intentional
# since empty or undef might occur in some buggy situations, but ' ' is
# quite unlikely.
#

sub player_ships {
  my($data) = @_;
  my($line, $ship1, $ship2, $pship1, $pship2, $rest);
  while ($line = getline($data->{fh})) {
      last if ($line =~ m|<H2>Other ships here:</H2>|);
  }
  message(" Other ships here");
  # Need to handle popcorn somewhere around here.
  while ($line = getline($data->{fh})) {
      if ($line eq "<H3>Details</H3>\n") {
	  ungetline($line);
	  return;
      }
      if ($line =~ m|^<A HREF=\"([^\"]*)\">(.*?)</A>(.*)meets\s*$|) {
	  $ship1 = $2;
	  $rest = $3;
	  player_ships_ship($data, $ship1);
	  if ($rest =~ m|\(guarding <A HREF=\"(.*?)\">(.*?)</A>\)|) {
	      $pship1 = $2;
	      player_ships_ship($data, $pship1);
	  } else {
	      $pship1 = ' ';
	    }
	  $line = getline($data->{fh});
	  if ($line =~ m|^<A HREF=\"(.*?)\">(.*?)</A>(.*)<BR>$|) {
		$ship2 = $2;
		$rest = $3;
		player_ships_ship($data, $ship2);
		if ($rest =~ m|\(guarding <A HREF=\"(.*?)\">(.*?)</A>\)|) {
		    $pship2 = $2;
		    player_ships_ship($data, $pship2);
		} else {
		    $pship2 = ' ';
		}
		player_ships_meeting($data, $ship1, $ship2, $pship1, $pship2);
	    } else {
		error("Unmatches 'meets' line");
	    }
      } elsif ($line =~ m|^<A HREF=\"(.*?)\">(.*?)</A>(.*)leftover<BR>$|) {
	  $ship1 = $2;
	  $rest = $3;
	  player_ships_ship($data, $ship1);
	  if ($rest =~ m|\(guarding <A HREF=\"(.*?)\">(.*?)</A>\)|) {
	      $pship1 = $2;
	      player_ships_ship($data, $pship1);
	  } else {
	      $pship1 = ' ';
	  }
	  player_ships_meeting($data, $ship1, ' ', ' ', $pship1, ' ', ' ');
      } else {
	  error("Unexpected line in ship meetings '$line'");
      }
  }
} # player_ship()

######################################################################
#
# Update ship locations and also sharing settings for configurations
# (which were already entered by update_ship()).
#

sub player_ships_ship {
    my($data, $ship) = @_;
    my($tablename);
    message(" updating sharing for shiploc and shipconfig for $ship");

    UpdateDataAndShared($data->{ship}, \%ShipLocTable, 'shiploc', $ship, {
	turn => $opt_t,
	ship => $ship,
	system => $data->{system}
    });

    foreach $tablename (@ShipConfigTables) {
	UpdateShared($data->{ship}, $tablename, @{$ShipIIDs{$ship}});
    }
    message("  Done updating.");
}

# Update ship meeting information. Note that ship1 should
# always be provided and unique for a turn.

sub player_ships_meeting {
    my($data, $ship1, $ship2, $pship1, $pship2) = @_;

    UpdateDataAndShared($data->{ship}, \%MeetingsTable, 'meetings', $ship1, {
	turn => $opt_t,
	system => $data->{system},
	ship1 => $ship1,
	ship2 => $ship2,
	protected1 => $pship1,
	protected2 => $pship2
	});
}

######################################################################
#
# Update shop data from the shop section of the player page.
# Note that prices are listed only in the player commands section.
#

sub player_shops {
  my($data) = @_;
  my($line, $system, $shopn);
  while ($line = getline($data->{fh})) {
      if ($line =~ m|^<H3>.*Favour.*</H3>$|) {
	  ungetline($line);
	  return;
      }
      if ($line =~ m|<TR><TH COLSPAN=4 ALIGN=CENTER>(.*) Shop-([0-9]+) \(\)</TH></TR>|) {
	  $system = $1;
	  $shopn = $2;
	  if ($data->{system} ne $system) {
	      error("Reporting data on $system Shop-$shopn, but in system $system!");
	  }
	  process_shop($data, $system, $shopn);
      }
  }
  error("Reached end of file while in player_shops()!");
} # player_shops()

sub process_shop {
    my($data, $system, $shopn) = @_;
    my($line, $item, $tech, $reliability, $yield, $capacity, $techre, $iid);

    message(" Processing $system Shop-$shopn.");

    $techre = TechRE();    
    while ($line = getline($data->{fh})) {
	if ($line =~ m|<P><STRONG>Mass = [0-9]+, Energy Yield = [0-9]+, Torpedo Stock = [0-9]+, Cargo capacity: [0-9]+ </STRONG><P>|) {
	    return;
	}
	if ($line =~ m|^<TR ALIGN=CENTER><TD>(.*?)\s*</TD><TD>($techre)</TD><TD>([0-9]+)%</TD><TD>([0-9]+)</TD></TR>$|i) {
	    $item = $1;
	    $tech = TechNameToLevel($2);
	    $reliability = $3;
	    $yield = $4;

	    $iid = UpdateData($data->{ship}, \%ModulesTable, 'modules', $item, {
		turn => $opt_t,
		loctype => "shop",
		loc => "$system Shop-$shopn",
		name => $item,
		type => ItemNameToType($item),
		tech => $tech,
		yield => $yield,
		reliability => $reliability
		});		
	    UpdateShared($data->{ship}, 'shopmodules', $iid);

	} elsif ($line =~ m|^<TR ALIGN=CENTER><TD>(.*?)\s*</TD><TD>([0-9]+)</TD><TD>Empty</TD><TD>0</TD></TR>|) {
	    $item = $1;
	    $capacity = $2;
	    $iid = UpdateData($data->{ship}, \%PodsTable, 'pods', $item, {
		turn => $opt_t,
		loctype => "shop",
		loc => "$system Shop-$shopn",
		name => $item,
		capacity => $capacity,
		resource => 'Empty',
		carrying => 0
		});
	    UpdateShared($data->{ship}, 'shippods', $iid);
	}
    }
    error("Reached end of file while in player_shop()!");
} # player_shop()

sub player_favour {
  my($data) = @_;
}

sub player_politics {
  my($data) = @_;
}

sub player_finances {
  my($data) = @_;
}

sub player_commands {
  my($data) = @_;
}


sub usage {
    print STDERR "Usage: $0 [-t turn]\n";
    exit;
}

######################################################################
#
# Read a line from passed file handle.
#
# By default, error if EOF.
# If extra arg is provided, return it instead of signaling an error.
#
# Works consistently ungetline()

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
    if ($#UngetLines >= 0) {
	return pop(@UngetLines);
    }
    $fh = $_[0];
    $ret = <$fh>;
    if (!defined($ret)) {
	if ($faileof) {
	    error("Unexpected end of file");
	} else {
	    return $sigeof;
	}
    }
    return $ret;
} # getline()

sub ungetline {
    my($line) = @_;
    push(@UngetLines, $line);
}

sub clearungetlines {
    @UngetLines = ();
}
  
sub isset {
    my($str) = @_;
    return defined($str) && $str !~ /^\s*$/;
}

######################################################################
#
# Read the database tables for this turn.
#

sub ReadDatabaseTables {
    rdb_general(\%ShipLocTable, 'shiploc', 'ship');
    rdb_general(\%MeetingsTable, 'meetings', 'ship1');
    rdb_general(\%SharedTable, 'shared', 'ship', 'iid');
    rdb_general(\%PlaguesTable, 'plagues', 'system');
    rdb_general(\%TradeTable, 'trade', 'locid');
    rdb_sharing();
    @ShipConfigTables = SelectAll("select m.tablename from sharingmap m, sharingtypes s where m.sharetypeid=s.sharetypeid and s.shortname='shipconfig';");
}


sub rdb_sharing {
    my($sth, $row);
    $sth = mydo("
select s.ship as sharer, map.tablename, p.ship as sharee from 
  sharingsettings s, 
  sharingships    p, 
  sharingmap      map,
  (select ship, max(turn) as turn from sharingsettings where turn<=? group by ship) m
 where 
  s.ship=m.ship   		     and 
  s.turn=m.turn   		     and 
  s.id=p.id       		     and 
  s.sharetypeid=map.sharetypeid",
		$opt_t);
    while ($row = $sth->fetchrow_hashref()) {
	push(@{$SharingTable{$row->{sharer} . ":" . $row->{tablename}}}, $row->{sharee});
    }
    $sth->finish();
}
    
sub rdb_general {
    my($h, $table, @keys) = @_;
    my($sth, $row, $key);
    $sth = mydo("select * from $table where turn=?;", $opt_t);
    while ($row = $sth->fetchrow_hashref()) {
	$key = join(":", map { $row->{$_} } @keys);
	$h->{$key} = $row;
    }
    $sth->finish();
}

sub UpdateDataAndShared {
    my($ship, $tablehash, $tablename, $key, $settings) = @_;
    my($iid);
    $iid = UpdateData($ship, $tablehash, $tablename, $key, $settings);
    UpdateShared($ship, $tablename, $iid);
}

sub UpdateData {
    my($ship, $tablehash, $tablename, $key, $settings) = @_;
    my(@settingkeys, @settingvalues, $iid, $sharee);
    
    @settingkeys = keys %{$settings};    
    @settingvalues = map { $settings->{$_} } @settingkeys;
    
    if (!exists($tablehash->{$key})) {
	mydo("insert into $tablename (" . 
	     join(", ", @settingkeys) . 
	     ") values (" . 
	     join(", ", map { "?" } @settingkeys) . 
	     ");", @settingvalues);
	# Set from database so default values are included
	$tablehash->{$key} = 
	    SelectOneRowAsHash("select * from $tablename where " . 
			       join(" and ", map { "$_=?" } @settingkeys) .
			       ";",
			       @settingvalues);
    }
    return $tablehash->{$key}{iid};
}

sub UpdateShared {
    my($ship, $tablename, @iids) = @_;
    my($iid, $sharee);

    foreach $sharee (@{$SharingTable{"$ship:$tablename"}}) {
	foreach $iid (@iids) {
	    if (!exists($SharedTable{"$sharee:$iid"})) {
		# Instead of writing to the database right away, write to
		# the sharedupdate tmp file. Once we're done, update
		# the database in one go.
		print $SharedUpdateTmpFH "$sharee\t$iid\t$opt_t\n";
		$SharedTable{"$sharee:$iid"} = [ ship => $sharee, iid=> $iid, turn => $opt_t ];
	    }
	}
    }
}
