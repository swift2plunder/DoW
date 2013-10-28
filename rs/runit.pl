#!/usr/bin/perl -w

use strict;
use FileHandle;
use Getopt::Std;

use dow;

use vars qw($opt_v);

my ($LogFH, $TopDir, $OPTS, $Verbose, $VerboseFlag);

$TopDir = '/Path/to/rs';
$LogFH = new FileHandle(">>$TopDir/log") or die "Couldn't open log file: $!";
$OPTS = '-O3 -funroll-loops -ffast-math';

$opt_v = 0;
getopts('v') or usage();

# If no arguments, default verbosity is false.
# If arguments are provided, they are donorids to run regardless of
# xeno and update settings, and default verbosity is true.

if ($#ARGV == -1) {
    $Verbose = 0;
} else {
    $Verbose = 1;
}

# The -v flag toggles verbosity.
if ($opt_v) {
    $Verbose = !$Verbose;
}

if ($Verbose) {
    $VerboseFlag = '-v';
} else {
    $VerboseFlag = '';
}

OpenDB();

logit("\n");
logit(`date`);

if ($#ARGV == -1) {
    RunAll();
} else {
    RunDonors(@ARGV);
}

CloseDB();

$LogFH->close();

sub RunDonors {
    my(@donorids) = @_;
    my($donorid);

    foreach $donorid (@donorids) {
	RunOne($donorid);
    }
}

sub RunAll {
    my(@donors, $donorid);
    foreach $donorid (SelectAll("select rss.donorid from rss, donors where updated=true and rss.donorid=donors.donorid and xeno=true;")) {
	RunOne($donorid);
	mydo("update rss set updated=false where donorid=?;", $donorid);
    }
}

sub RunOne {
    my($donorid) = @_;
    my($donor);
    $donor = SelectOneRowAsHash("select * from donors where donorid=?;", $donorid);
    chdir("$TopDir");
    unlink('shipdata.c', 'rs.o', 'list.o', 'rs');
    logit("Generating $donor->{ship} ($donorid)\n");
    system("$TopDir/genplayer.pl $donorid");
    logit("Compiling\n");
    system("gcc $OPTS -c rs.c -o rs.o");
    system("gcc $OPTS -c lists.c -o lists.o");
    system("gcc $OPTS rs.o lists.o -lpq -lgc -ldl -o rs");
    logit("Starting the simulator\n");
    $LogFH->close();
    system("$TopDir/rs $VerboseFlag > $donor->{donorid}.list");
    $LogFH = new FileHandle(">>$TopDir/log") or die "Couldn't open log file: $!";
    logit("Done.\n\n");
}

sub logit {
    print $LogFH @_;
    if ($Verbose) {
	print STDERR @_;
    }
}



