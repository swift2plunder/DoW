#!/usr/bin/perl -w
#
# I seem to need to do this a lot...

use strict;
use dow;

my $Turn;

OpenDB();

if ($#ARGV == -1) {
    $Turn = GetLatestTurn();
} elsif ($#ARGV == 0) {
    $Turn = $ARGV[0];
} elsif ($#ARGV == 1 && $ARGV[0] eq '-t') {
    $Turn = $ARGV[1];
} else {
    print STDERR "Usge: cleardow.pl [[-t] turn]\n";
    exit;
}

ClearTurn();

CloseDB();

exit;

sub GetLatestTurn {
    return SelectOne("select max(turn) from turnupdate;");
}

sub ClearTurn {
    print "Clearing turn $Turn\n";
    dd('turnupdate');
    dd('shop');
    dd('trade');
    dd('adventures');
    dd('terminals');
    dd('plagues');
    dd('shipdata');
    dd('skills');
    dd('criminals');
    dd('enemies');
    dd('meetings');
    dd('shiploc');
    dd('rogues');
    dd('pods');
    dd('modules');
    dd('influence');
    dd('flags');
    dd('fragments');
 #   dd('shipconfig');	#  Comment this out UNLESS you also remove the cache entries.
    print "Resetting sysplagues\n";
    mydo("update sysplagues set level=NULL where turn=?;", $Turn);
    mydo("update sysplagues set turn=NULL where turn=?;", $Turn);

    print "Clearing artifacts\n";
    mydo("delete from curses where artifactid in (select artifactid from artifacts where turn=?);", $Turn);
    mydo("delete from keys where artifactid in (select artifactid from artifacts where turn=?);", $Turn);
    dd('artifacts');
    dd('medicine');
    dd('systemviewed');
    print "Clearing probes\n";
    mydo("delete from probes;");
    
    dd('activeships');
    dd('traces');
    dd('favour');

    dd('popcorn');

    print("Done\n");
}

sub dd {
    my($msg) = @_;
    print " Deleteing $msg.  Before: ";
    pc($msg);
    mydo("delete from $msg where turn=?;", $Turn);
    print "   After: ";
    pc($msg);
    print "\n";
}

sub pc {
    my($msg) = @_;
    print SelectOne("select count(*) from $msg where turn=?;", $Turn);
}
    
    

sub error {
    my($msg) = @_;
    print STDERR "$msg\n";
    exit;
}

sub warning {
    my($msg) = @_;
    print STDERR "$msg\n";
}

sub message {
    my($msg) = @_;
    print "$msg\n";
}

