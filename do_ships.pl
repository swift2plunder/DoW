#!/usr/bin/perl -w
#

use strict;
use DBI;
use FileHandle;
use DirHandle;
use Getopt::Std;

use dow;

use vars qw($opt_t $opt_h);

my $Top = '/Path/to/tbg';
my @UngetLines;		# Used with getline/ungetline

OpenDB();

$opt_t = SelectOne("select max(turn) from turnupdate;");
getopts('ht:') or usage();
usage() if $opt_h;

do_ships();

CloseDB();

exit;

sub usage {
    print STDERR "Usage: do_ships.pl [-t turn]\n";
    exit;
}

sub do_ships {
    my($dh, $fn);
    $dh = new DirHandle("$Top/ships/$opt_t") or die "Couldn't open ship dir '$Top/ships/$opt_t'";
    print "\nProcessing ships for turn $opt_t.\n";
    while ($fn = $dh->read()) {
	next if $fn !~ /\.html$/;
	process_ship("$Top/ships/$opt_t/$fn");
    }
    $dh->close();
}

sub process_ship {
    my($path) = @_;
    my($fh, $line, $ship);
    my($name, $tech, $reliability, $yield, $broken, $techlevel);
    my($capacity, $resource, $carrying);
    my($powerrank, $combatmass, $techre);
    $fh = new FileHandle("$path") or die "Couldn't open $path: $!";
    $line = getline($fh);
    if ($line !~ m|^<HTML><HEAD><TITLE>(.*), Turn $opt_t</TITLE></HEAD>$|) {
	die "Header line '$line' incorrect.";
    }
    $ship = $1;
    if (ExistsSelect("select * from powerrank where ship=? and turn=?;", $ship, $opt_t)) {
	print "Ship $ship already processed. Skipping.\n";
	$fh->close();
	return;
    }
    print "Updating ship $ship\n";

    $techre = TechRE();
    $powerrank = 0;
    $combatmass = 0;
    while ($line = getline($fh)) {
	# Extract modules
	if ($line eq "<TR><TH>Component</TH><TH>Tech</TH><TH>Reliability</TH><TH>E Yield</TH></TR>\n") {
	    while ($line = getline($fh)) {
		if ($line =~ m!^<TR ALIGN=CENTER><TD>(.*?)\s*</TD><TD>(primitive|basic|mediocre|advanced|exotic|magic)</TD><TD>\s*([0-9]+)%\s*</TD><TD>([0-9]+)</TD></TR>!i) {
		    $name = $1;
		    $tech = $2;
		    $reliability=$3;
		    $yield=$4;
		    if ($name =~ /\(U\)$/) {
			$broken = 1;
			$name =~ s/\(U\)$//;
		    } else {
			$broken = 0;
		    }
		    $techlevel = TechNameToLevel($tech);
#		    print STDERR "$name, $tech, $reliability, $yield, $techlevel\n";
#		    mydo("insert into modules (turn, item, type, tech, yield, reliability, ship) values(?, ?, ?, ?, ?, ?, ?);",
		    mydo("insert into nmods (turn, loctype, loc, name, broken, type, tech, yield, reliability) values(?, 'ship', ?, ?, ?, ?, ?, ?, ?);",
			 $opt_t, $ship, $name, $broken, GetShopItemType($name), $techlevel, $yield, $reliability);
		    $combatmass += 1;
		    # Demo and broken modules do not count for powerrank
		    if ((! $broken) && ($name !~ /D$/)) {
			$powerrank += $techlevel;
		    }
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
		    mydo("insert into pods (turn, name, capacity, n, resource, ship) values (?, ?, ?, ?, ?, ?);", $opt_t, $name, $capacity, $carrying, $resource, $ship);
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
	} elsif ($line eq "</CENTER></BODY></HTML>\n") {
	    last;
	}
    }
    $fh->close();
    mydo("insert into powerrank (ship, turn, powerrank) values (?, ?, ?);",
	 $ship, $opt_t, $powerrank);
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
    # According to SST: In memory of the passing of Arthur C. Clarke, all sufficiently advanced technology has been dimmed galaxy wide. Requiescat in pace.
    # It appears magic modules have <FONT COLOR="#808000">Magic</FONT> around them.
    # 03/20/08

    $ret =~ s|<FONT COLOR=\"\#808000\">Magic</FONT>|Magic|g;

    return $ret;
}

sub ungetline {
    my($line) = @_;
    push(@UngetLines, $line);
}

sub error {
    print STDERR "Error: ", join(" ", @_), "\n";
    exit;
}
