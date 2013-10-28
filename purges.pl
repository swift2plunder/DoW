#!/usr/bin/perl -w

use strict;
use Getopt::Std;
use FileHandle;
use dow;

use vars qw($opt_h $opt_t);

OpenDB();

$opt_h = 0;
$opt_t = SelectOne("select max(turn) from turnupdate;");
getopts("ht:") or usage();
($#ARGV == -1) or usage();
(!$opt_h) or usage();

DoCheckPurges();

CloseDB();

sub usage {
    print STDERR <<'EndOfUsage';

Usage: purges.pl -t turn

     -t turn   Turn    Which turn to check.

EndOfUsage
}

sub DoCheckPurges {
    my($dsth, $drow, $ssth, $srow, @systems, $system, $pid);
    my(%systemtopurges); # Map of system name to a boolean for if the data is shared.

    # Clear existing data, if any.

    foreach $pid (SelectAll("select purgeid from purgedsystems where turn=?;", $opt_t)) {
	mydo("delete from purgesuspects where purgeid=?;", $pid);
    }
    mydo("delete from purgedsystems where turn=?;", $opt_t);

    # First, figure out which systems were purged.

    $dsth = mydo("select d.* from donors d, turnupdate t where d.donorid=t.donorid and turn=?;", $opt_t);
    while ($drow = $dsth->fetchrow_hashref()) {
	$ssth = mydo("select system from terminals where system!='None' and donorid=? and turn=? and system not in (select system from terminals where donorid=? and turn=?);", $drow->{donorid}, $opt_t-1, $drow->{donorid}, $opt_t);
	while ($srow = $ssth->fetchrow_hashref()) {
	    if ($drow->{purgers}) {
		$systemtopurges{$srow->{system}} = 1;
	    } elsif (!exists($systemtopurges{$srow->{system}})) {
		$systemtopurges{$srow->{system}} = 0;
	    }
	}
    }

    # Now, compute suspects for each system.
    @systems = keys(%systemtopurges);
    print "The following systems where purged on turn $opt_t: ";
    print join(", ", @systems), "\n";
    foreach $system (@systems) {
	if ($systemtopurges{$system}) {
	    mydo("insert into purgedsystems values(default, ?, ?, true);",
		 $system, $opt_t);
	} else {
	    mydo("insert into purgedsystems values(default, ?, ?, false);",
		 $system, $opt_t);
	}
	$pid = GetSequence("purgedsystems_purgeid");

	if (CheckSST($opt_t, $system)) {
	    mydo("insert into purgesuspects values($pid, 'Dybuk Logic Bomb', true);");
	} else {
	    $ssth = mydo("select ship, purgers from shiploc where turn=? and system=? and ship !~ \'[0-9]\$\' order by ship;", $opt_t-1, $system);
	    while ($srow = $ssth->fetchrow_hashref()) {
		if ($srow->{purgers}) {
		    mydo("insert into purgesuspects values(?, ?, true);", 
			 $pid, $srow->{ship});
		} else {
		    mydo("insert into purgesuspects values(?, ?, false);", 
			 $pid, $srow->{ship});
		}
	    }
	}
    }
}

sub CheckSST {
    my($turn, $system) = @_;
    my($fh, $line);
    $fh = new FileHandle("/Path/to/sst/$turn.html") or die "Couldn't open sst file $turn.html: $!";
    while ($line = <$fh>) {
	chop($line);
	if ($line eq "<HR>Logic-bomb used at $system!") {
	    $fh->close();
	    return 1;
	}
    }
    $fh->close();
    return 0;
}	
