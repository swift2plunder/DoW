#!/usr/bin/perl -w
#
# Start the whole download/update process.
# This script does not call download.pl or update.pl, it just
# "hotstarts" the tables that control the process.
#
# Hack to determine which turn we're on:
# Grab the SST and check the turn heading. If it already exists, then
# the turn probably hasn't updated yet. Note that it just throws
# away the SST immediately, since download.pl is responsible for
# downloading. I wish there were a better way to determine the turn.
#

use strict;
use Getopt::Std;
use LWP::Simple;

use dow2;

use vars qw($opt_t);

my @OrigARGV = @ARGV;

my($Turn, $ArchivePath, $TBG_URL);

getopts('t:') or usage();

OpenDB("dow2");

$TBG_URL = SelectOne("select tbgurl from params;");
if (defined($opt_t)) {
    $Turn = $opt_t;
} else {
    $Turn = GetCurrentTurnFromSST();
}

OpenLogs("start", $Turn);
message("\n----------\nstart.pl called with arguments '" . join(" ", @OrigARGV) . "' on " .  `date`);

mydo("update params set processturn=$Turn;");

$ArchivePath = SelectOne("select topdir from params;") . "/" . SelectOne("select archive from params;") . "/$Turn";

start_misc();
start_donors();

message("start.pl finished on " . `date`);
CloseLogs();
CloseDB();

exit;

# All subs below here.

sub usage {
    print STDERR "\nUsage: $0 -t turn\n";
    print STDERR "\n\tStart the turn update.\n";
    exit;
}

# Try to get the current turn. Die horribly if it appears to be wrong.

sub GetCurrentTurnFromSST {
    my($sst, $turn);
    $sst = myget("$TBG_URL/times.html");
    if (!defined($sst)) {
	print STDERR "Couldn't download SST '$TBG_URL/times.html' (to check current turn.\n";
	exit();
    }
    if ($sst =~ m|^<H1>Issue ([0-9]+) - Stardate [0-9.]+</H1>$|m) {
	$turn = $1;
	if (ExistsSelect("select * from downloadfiles where type='SST' and turn=$turn and status != 'Start';")) {
	    print STDERR "Turn $turn has already been started. Skipping.\n";
	    exit();
	} else {
	    return $turn;
	}
    } else {
	print STDERR "Couldn't extract turn from SST.\n";
	exit();
    }
}    

sub start_misc {
    my($oid);
    $oid = InsertUnique("downloadfiles", 
			{ turn => $Turn,
			  filename => "times.html",
			  url =>  "$TBG_URL/times.html",
			  status => 'Start',
			  type => 'SST' },
			qw ( turn filename ) );
    message("Queued SST $oid");
    $oid = InsertUnique("downloadfiles",
			{ turn => $Turn,
			  filename => "alias.html",
			  url => "$TBG_URL/alias.html",
			  status => 'Start',
			  type => 'Alias File' },
			qw ( turn filename ) );
    message("Queued alias $oid");			  
}

sub start_donors {
    my($sth, $row, $oid);
    $sth = mydo("select dat.ship, secreturl from donors, donordata dat where secreturl is not null and donors.ship=dat.ship;");
    while ($row = $sth->fetchrow_hashref()) {
	# Check here if it's valid...  ???
	$oid = InsertUnique("downloadfiles",
			    { turn => $Turn,
			      filename => NameToFilename($row->{ship}) . ".player.html",
			      url => $row->{secreturl},
			      status => 'Start',
			      type => 'Player',
			      name => $row->{ship} },
			    qw( turn name type ));
	message("Queued player $row->{ship} $oid");
    }
    $sth->finish();
}

# Get the URL and return it as a string.
# Try 3 times. If all three fail, return undef.

sub myget {
    my($url) = @_;
    my($try, $ret);
    for ($try = 0; $try < 3; $try++) {
    	$ret = get($url);
	if (!defined($ret)) {
	    warning("myget($url) failed, try $try");
	} else {
	    return $ret;
	}
    }
    warning("myget($url) failed too many times. Giving up.");
    return undef;
}
