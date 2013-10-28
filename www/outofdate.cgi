#!/usr/bin/perl -w
#
# Show systems that are out of date.
#
# I've removed some obfuscation bits of this code for the public release.
#

use strict;
use Getopt::Std;

use dow;

use vars qw($opt_t $opt_m);

my($Donor);

$Donor = ProcessDowCommandline();

$opt_t = SelectOne("select max(turn) from turnupdate;");

getopts('mt:') or usage();

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: outofdate.cgi?-t+turn+-m");
}

sub GeneratePage {
    my($sth, $row, $system, @named, @unnamed, $sysn, %named_turn, %unnamed_turn);
    my($vsth, $vrow, $tsth, $trow);

    # For each system, figure out when it was last visited and when
    # trade data was updated.

    $sth = mydo("select system from starcoords order by system;");
    $vsth = myprep("select max(turn) from shiploc, donors where system=? and shiploc.ship=donors.ship and turn<=?;");
    $tsth = myprep("select max(turn) from trade where system=? and turn<=?;");
    while ($row = $sth->fetchrow_hashref()) {

	$system = $row->{system};

	myex($vsth, $system, $opt_t);
	$vrow = $vsth->fetchrow_hashref();
	myex($tsth, $system, $opt_t);
	$trow = $tsth->fetchrow_hashref();

	if ($system =~ /^Star \#([0-9]+)$/) {
	    $sysn = $1;
	    if (!isset($vrow, 'max') || $vrow->{max} <= $opt_t-10) {
		push(@unnamed, $sysn);
		$unnamed_turn{$sysn} = $vrow->{max};
	    }
	} elsif (!isset($vrow, 'max') || $vrow->{max} <= $opt_t-8 ||
		 (isset($trow, 'max') && $trow->{max} <= $opt_t-3)) {
	    push(@named, $system);
	    $named_turn{$system} = $vrow->{max};
	}
    }

    $sth->finish();
    $tsth->finish();
    $vsth->finish();

    add(DOW_HTML_Header($Donor, "DOW - System Needing Data"));
    add("<h1>DOW - Systems Needing Data</h1>");
    if ($opt_m) {
	add("Show <a href=\"outofdate.cgi\">List View</a><p><hr><p>\n");
	@unnamed = map { "Star #$_" } @unnamed;
	add(MakeMapImage($Donor->{ship}, \@unnamed, "biggreen.gif", \@named, "bigred.gif"));
	add("\n<hr>\n");
	add("<img src=\"bigred.gif\"> - Out of Date \"Named\" system<br>\n");
	add("<img src=\"biggreen.gif\"> - Out of Date \"Unnamed\" system<br>\n");
    } else {
	add("Show <a href=\"outofdate.cgi?-m\">Map View</a><p><hr><p>\n");
	foreach $system (sort @named) {
	    add("<a href=\"system.cgi?" . UncanonicalizeSystem($system) . "\">$system</a>");
	    add("<br>\n");
	}
	add("<p>\n");
	foreach $system (sort { $a <=> $b } @unnamed) {
	    add("<a href=\"system.cgi?S$system\">Star \#$system</a>");
	    add("<br>\n");
	}
    }
    add(DOW_HTML_Footer($Donor));
}

sub isset {
    my($row, $str) = @_;
    return exists($row->{$str}) && defined($row->{$str}) && $row->{$str} !~ /^\s*$/;
}

# Return the key whose value is minimum
sub getmin {
    my(%h) = @_;
    my(@h);
    @h = sort { $h{$a} <=> $h{$b} } keys %h;
    return $h[0];
}
