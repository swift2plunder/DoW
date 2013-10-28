#!/usr/bin/perl -w
#
# Show ship summary information
#
# The code for computing skill levels is truly horrible.
#

use strict;
use FileHandle;

use dow;

my($Donor, $Ship, @CurseLabel, @Weapons, @Ranges, $AlienRE);

@Weapons = qw (Ram Gun Disruptor Laser Missile Drone Fighter);
@Ranges = qw (Adjacent Close Short Medium Long Distant Remote);

@CurseLabel = qw (Wd Id Sn Cl Ls Sb Sh Wp);

$Donor = ProcessDowCommandline();

if ($#ARGV != 0) {
    usage();
}

$Ship = $ARGV[0];
$Ship =~ s/\\//g;

GeneratePage();
PrintPageData();

CloseDB();

exit;

# Given a weapon NAME, return the range NUMBER (not name)
sub WeaponToRangeI {
    my($name) = @_;
    my($i);
    for ($i = 0; $i <= $#Weapons; $i++) {
	if ($name =~ /^$Weapons[$i]/i) {
	    return $i;
	}
    }
    return -1;
}

sub WeaponFirepower {
    my($name) = @_;
    my($i);
    for ($i = 0; $i <= $#Weapons; $i++) {
	if ($name =~ /^$Weapons[$i]/i) {
	    return 5*(7-$i);
	}
    }
    herror("WeaponFirepower failed to find a weapon. This shouldn't happen");
}
    
sub usage {
    herror("Usage: shipsummary.cgi?Ship%20name");
}

sub GeneratePage {
    my($retturn, $race, $data, $turn, $area, $ex);
    $turn = SelectOne("select max(turn) from turnupdate;");
    add(DOW_HTML_Header($Donor, "DOW - Summary of $Ship"));
    add("<h1>Summary of $Ship</h1>");
    $race = RaceOfShip($Ship);
    if (ExistsSelect("select * from banned where ship=?;", $Ship)) {
	add("<font size=\"-1\">Banned from DOW: " . SelectOne("select description from banned where ship=?;", $Ship) . ".</font>\n");
    }
    if (!ExistsSelect("select * from activeships where ship=? and turn=?;", $Ship, $turn) && !defined($race)) {
	add("<font size=\"-1\">Retired");
	$retturn = SelectOne("select max(turn) from activeships where ship=?;",
			     $Ship);
	if (defined($retturn) && $retturn > 0) {
	    add(" on turn " . (1+$retturn));
	}
	add("</font>\n");
    }
    if (defined($race)) {
	add("<font size=\"-1\">Of the </font><a href=\"alien.cgi?$race\"><font size=\"-1\">$race</font></a><font size=\"-1\"> people.</font></a>\n");
    }
    DoConfigSummary();
    DoLocationSummary();
    if (!defined($race)) {
	DoInfluenceSummary();
	DoComments();
    }
    add(DOW_HTML_Footer($Donor));
}

sub DoComments {
    my($sth, $row, @scorestr);
    @scorestr = qw(Great Good Neutral Poor Bad);
    add("<hr><p>DOW Member comments about $Ship");
    add("<p><a href=\"viewcomments.cgi?$Ship\">View all comments</a> &nbsp; &nbsp;");
    add("<a href=\"entercomments.cgi?$Ship\">Enter a new comment</a>\n");
    $sth = mydo("select count(score), avg(score), min(score), max(score) from shipcomments where ship=?;", $Ship);
    $row = $sth->fetchrow_hashref();
    if (!defined($row) || $row->{count} == 0) {
	add("<p>No comments for $Ship have been entered by DOW members.\n");
    } else {
	add(sprintf("<p>About %d comment%s with an average score of %.1f (%s) (min %d, max %d) have been entered by DOW members.\n", 
		    $row->{count}, 
		    ($row->{count} > 1) ? "s" : "", 
		    $row->{avg}, $scorestr[int($row->{avg} + 0.5)-1], 
		    $row->{min}, $row->{max}));
    }
}


sub DoLocationSummary {
    my($sth, $row);
    add("<hr>");
    if (! $Donor->{shiploc}) {
	add("<p>No location data is available because you don't donate location data.");
	return;
    }

    add("<p>Full location history: <a href=\"shiploc.cgi?$Ship\">List</a> &nbsp; | &nbsp; <a href=\"shiplocmap.cgi?$Ship\">Map</a>\n");
    
    $sth = mydo("select distinct on (ship) * from shiploc where ship=? and system != 'Holiday Planet' and donated=true order by ship, turn desc;", $Ship);

    $row = $sth->fetchrow_hashref();
    $sth->finish();

    if (defined($row)) {
	add("<p>$Ship was last seen at <a href=\"system.cgi?" . 
	    UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a> on turn $row->{turn}.\n");
    } else {
	add("<p>No donated location data for $Ship is available.\n");
    }
}

sub DoInfluenceSummary {
    my($totalvotes);

    add("<hr><p>");
    if (! $Donor->{influence}) {
	add("No influence data is available because you don't donate influence information.\n");
	return;
    }
    add("<p><a href=\"influenceship.cgi?$Ship\">Show full influence data</a>\n");

    $totalvotes = SelectOne("select sum(votes) from (select distinct on (location) * from influence where donated=true order by location, turn desc) as orig where ship=?;", $Ship);
    add("<p>$Ship controls ");
    if (!defined($totalvotes) || $totalvotes == 0) {
	add("no votes");
    } elsif ($totalvotes == 1) {
	add("1 vote");
    } else {
	add("$totalvotes votes");
    }
    add(".\n");
}

sub DoConfigSummary {
    my($sth, $row, $line, $fh, $gotbody, %percentages, $name, $tech, $type);
    my($totalmass, @techtotal);
    my($techre, %bless, %curse, $curses, @modskill, @shipskill, @useplus);
    my($i, $key, $engskill, $sciskill, $medskill, $weapskill, $l, $p, $m);
    my(@firepower, $rangei, $powerrank);

    @firepower = qw(0 0 0 0 0 0 0 0);
    $powerrank = 0;
    add("<hr>");
    if (! $Donor->{shipconfig}) {
	add("<p>No configuration data is available because you don't donate configuration data.");
	return;
    }
    $sth = mydo("select * from shipconfig where donated=true and ship=? order by turn desc limit 1;", $Ship);

    $row = $sth->fetchrow_hashref();
    $sth->finish();
    # $row now contains the shipconfig line for $Ship

    if (!defined($row)) {
	add("<p>No donated ship configuration information for $Ship is available.\n");
	return;
    }

    $fh = new FileHandle($row->{path});
    if (!$fh) {
	herror("Couldn't get ship config from cache. This shouldn't happen!");
    }
    $gotbody = 0;
    while ($line = <$fh>) {
	if ($line eq "<BODY TEXT=\"Yellow\" BGCOLOR=\"Black\" LINK=\"White\" VLINK=\"Cyan\"><CENTER>\n") {
	    $gotbody = 1;
	    last;
	}
    }
    if (!$gotbody) {
	herror("Failed to find body line in ship config!");
    }

    add("<p><a href=\"shipconfig.cgi?$Ship\">Show full configuration</a> &nbsp; ");
    add(" &nbsp; (Ship configuration from turn $row->{turn})\n");

    $techre = TechRE();
    $totalmass = 0;

    while ($line = <$fh>) {
	last if ($line eq "</CENTER></BODY></HTML>\n");
	if ($line =~ /(Warp ([0-9]+)%, Impulse ([0-9]+)%, Sensor ([0-9]+)%, Cloak ([0-9]+)%, Life Support ([0-9]+)%, Sickbay ([0-9]+)%, Shield ([0-9]+)%, Weapon ([0-9]+)%)/) {
	    add("<br>$1\n");
	    $percentages{wd} = $2;
	    $percentages{id} = $3;
	    $percentages{sn} = $4;
	    $percentages{cl} = $5;
	    $percentages{ls} = $6;
	    $percentages{sb} = $7;
	    $percentages{sh} = $8;
	    $percentages{wp} = $9;
	} elsif ($line =~ /<TR ALIGN=CENTER><TD>(.*?)\s*<\/TD><TD>($techre)<\/TD><TD>\s*([0-9]+)%<\/TD><TD>([0-9]+)<\/TD><\/TR>/i) {
	    $name = $1;
	    $tech = TechNameToLevel(lc($2));
	    $type = GetShopItemType($name);
	    if ($type > 8) {
		$type = 8;
	    }
	    if ($name !~ /\(U\)/) {
		$techtotal[$type-1] += $tech;
		$powerrank += $tech;
		$rangei = WeaponToRangeI($name);
		if ($rangei >= 0) {
		    for ($i = 0; $i <= $rangei; $i++) {
			$firepower[$i] += $tech*WeaponFirepower($name);
		    }
		}
	    }
	} elsif ($line =~ /(Mass = ([0-9]+), Energy .*? = [0-9]+, Torpedo Stock = [0-9]+, Cargo capacity: [0-9]+)/i) {
	    # Energy COST or Energy YIELD (changed around turn 1660)
	    add("<br>$1\n");
	    $totalmass += $2;

	    # Pods
	} elsif ($line =~ m!<TR ALIGN=CENTER><TD>.*</TD><TD>([0-9])</TD><TD>.*</TD><TD>[0-9]</TD></TR>!) {
	    $powerrank += $1;

	    # Artifacts
	} elsif ($line =~ m!<TR ALIGN=CENTER><TD>.*?</TD><TD>([A-Z][a-z])</TD><TD>([a-zA-Z]+)</TD><TD>[0-9]+</TD>!) {
	    # Hypothesis: Artifacts don't count in mass...
	    $totalmass -= 1;
	    $bless{lc($1)} = 1;
	    $curses = lc($2);
	    if ($curses ne "none") {
		for ($i = 0; $i < length($curses); $i+=2) {
		    $curse{substr($curses, $i, 2)} = 1;
		}
	    }
	} elsif ($line =~ m|<TR><TH COLSPAN=4 ALIGN=CENTER>|) {
	    $line .= <$fh>;
	    $line =~ s/\n/ /g;
	    if ($line =~ m|<TR><TH COLSPAN=4 ALIGN=CENTER>\s*(.*?)\s*</TH></TR>|) {
		add("<p>Flag: &nbsp; $1");
	    } else {
		add("<p>(DEBUG) Failed to extract flag from '" . QuoteHTML($line) . "'\n");
	    }
	}
    }

    add("<br/>Power rank: $powerrank\n");

    $fh->close();

    @shipskill = qw(0 0 0 0 0 0 0 0);
    @useplus = ('','','','','','','','');
    for ($i = 0; $i <= $#techtotal; $i++) {
	if (defined($techtotal[$i])) {
	    $modskill[$i] = int(100.0 * $techtotal[$i]/$totalmass);
	    $l = lc($CurseLabel[$i]);
	    $m = $modskill[$i];
	    $p = $percentages{$l};
	    if (exists($curse{$l})) {
		$p = $p * 2;
	    }
	    if (exists($bless{$l})) {
		$p = $p / 1.5;
	    }
	    $shipskill[$i] = int($p - $m + 0.5);
	    if ($shipskill[$i] >= 2*$modskill[$i]) {
		$useplus[$i] = '+';
	    }
	}
    }

    if ($shipskill[0] > $shipskill[1]) {
	$engskill = $shipskill[0] . $useplus[0];
    } else {
	$engskill = $shipskill[1] . $useplus[1];
    }

    if ($shipskill[2] > $shipskill[3]) {
	$sciskill = $shipskill[2] . $useplus[2];
    } else {
	$sciskill = $shipskill[3] . $useplus[3];
    }

    if ($shipskill[4] > $shipskill[5]) {
	$medskill = $shipskill[4] . $useplus[4];
    } else {
	$medskill = $shipskill[5] . $useplus[5];
    }

    if ($shipskill[6] > $shipskill[7]) {
	$weapskill = $shipskill[6] . $useplus[6];
    } else {
	$weapskill = $shipskill[7] . $useplus[7];
    }


    add("<p>Skill Estimates: &nbsp; &nbsp; &nbsp; \n");
    add("Engineering: $engskill &nbsp; &nbsp; &nbsp; \n");
    add("Science: $sciskill &nbsp; &nbsp; &nbsp; \n");
    add("Medical: $medskill &nbsp; &nbsp; &nbsp; \n");
    add("Weaponry: $weapskill\n");
    add("<p>Firepower: &nbsp; &nbsp; ");
    for ($i = 0; $i <= $#Ranges; $i++) {
	add("$Ranges[$i]: $firepower[$i] &nbsp; \n");
    }
} # DoConfigSummary()
