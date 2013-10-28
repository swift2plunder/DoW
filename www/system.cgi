#!/usr/bin/perl -w
#
# Show system info.
#

use strict;

use dow;

my ($System, $Donor, $Turn);

$Donor = ProcessDowCommandline();

if ($#ARGV != 0) {
    usage();
}

$System = CanonicalizeSystem($ARGV[0]);

my @TechLevels = qw( Primitive Basic Mediocre Advanced Exotic Magic );

$Turn = SelectOne("select max(turn) from turnupdate where donorid=?", $Donor->{donorid});

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: system.cgi?SystemName\n<br> &nbsp; (e.g. system.cgi?S30)");
}

sub GeneratePage {
    my($terrain, $sys);
    add(DOW_HTML_Header($Donor, "DOW System Information on $System for $Donor->{ship}"));
    $terrain = SelectOne("select terrain from terrain where system=?;", $System);
    add("<h1>$System ($terrain terrain)</h1>\n");

    DoJumpCost();

    add("<hr>\n");

    DoHomeworld();
    DoStarnet();
    DoPlague();
    DoCriminals();
    DoRogues();
    DoStargates();
    DoStatics();

    DoDOWVisit();
    add("<p><a href=\"sightings.cgi?" . UncanonicalizeSystem($System) . "\">Ship sightings</a>");
    add(" &nbsp; | &nbsp; <a href=\"influencesys.cgi?" . UncanonicalizeSystem($System) . "\">Influences</a>");
    add(" &nbsp; | &nbsp; <a href=\"advhist.cgi?" . UncanonicalizeSystem($System) . "\">Adventure History</a>\n");

    $sys = UncanonicalizeSystem($System);
    if ($sys =~ /^S[0-9]+$/) {
	$sys =~ s/^S/S_/;
    }
    add("<br><a href=\"http://www.remtech.org/ScAvenger/planets/$sys.html\">View System</a> (courtesy of ScAvenger)");
    

    DoAdventures();

    DoTradeData();

    DoShopData();

    if (SelectOne("select mapinsys from prefs where donorid=?;", $Donor->{donorid})) {
	DoMap();
    }

    add(DOW_HTML_Footer($Donor));
}
   

sub DoMap {
    my($sth, $row, @gsys, @sys);
    $sth = mydo("select * from stargates where system1=?;", $System);
    while ($row = $sth->fetchrow_hashref()) {
	push(@gsys, $row->{system2});
    }
    $sth->finish();
    push(@sys, $System);
    add("<hr>");
    add(MakeMap($Donor->{ship}, \@sys, \@gsys));
    add("<hr>");
    add("<img src=\"bigred.gif\">Viewed System ($System)<br>");
    add("<img src=\"biggreen.gif\">Stargate from $System<br>");

}

sub DoStatics {
    my($sth, $row, @items);

    # DOW voted for popcorn to not be tracked.
    if ($Donor->{admin}) {
	add("<p>\n");
	$row = SelectOneRowAsHash("select * from popcorn order by turn desc limit 1;");
	if (CanonicalizeSystem($row->{system}) eq $System) {
	    if ($Turn == $row->{turn}) {
		add("The Popcorn source: ");
	    } else {
		add("The most recently known Popcorn source (turn $row->{turn}):");
	    }
	    add("   Impulse " . $row->{impulse} . "%");
	    add("   Sensor " . $row->{sensor} . "%");
	    add("   Shield " . $row->{shield} . "%");
	    add("<br>\n");
	}
    }

    $sth = mydo("select * from statics where system=? order by item", $System);
    $row = $sth->fetchrow_hashref();
    if (!defined($row)) {
	$sth->finish();
	return;
    }
    add("<p>Locations of interest: ");
    for (;;) {
	push(@items, "<a href=\"loc.cgi?$row->{item}\">$row->{item}</a>");
	$row = $sth->fetchrow_hashref();
        last if !defined($row);
    }
    add(join(", ", @items));
    add("<br>");
    $sth->finish();
}

sub DoDOWVisit {
    my($sth, $row, $tot, $n);
    if ($Donor->{admin}) {
	$sth = mydo("select max(turn) from donors, shiploc where system=? and donors.ship=shiploc.ship;", $System);
	$row = $sth->fetchrow_hashref();
	if (!defined($row) || !exists($row->{max}) || !defined($row->{max})) {
	    add("<p>$System never visited by a DOW ship. ");
	} else {
	    add("<p>$System last visited by a DOW ship on turn $row->{max}. ");
	}
	$sth->finish();
    }

    $tot = 0;
    $n = 0;
    $sth = mydo("select * from systemviewed where system=?;", $System);
    while ($row = $sth->fetchrow_hashref()) {
	$tot += 
	    SelectOne("select count(*) from shiploc where system=? and turn=?;",
		      $System, $row->{turn});
	$n++;
    }
    $sth->finish();
    if ($n > 0) {
	add(sprintf("<br>Visitations average %.1f ships per turn (%d samples).", $tot/$n, $n));
    }
}

sub DoHomeworld {
    my($sth, $row);
    $sth = mydo("select * from aliens where system=?;", $System);
    $row = $sth->fetchrow_hashref();
    if (!defined($row)) {
	return;
    }
    if (ExistsSelect("select who from enemies where donorid=? and turn=? and who=?;", $Donor->{donorid}, $Turn, $row->{race})) {
	add("<a href=\"alien.cgi?$row->{race}\">$row->{race}</a> Homeworld ($row->{alignment}, $row->{area}, your enemy)<p>");
    } else {
	add("<font color=\"#008000\"><a href=\"alien.cgi?$row->{race}\">$row->{race}</a> Homeworld ($row->{alignment}, $row->{area}, not currently your enemy)</font><p>");
    }
    $sth->finish();
}

sub DoStargates {
    my($sth, $row);
    $sth = mydo("select * from stargates where system1=?;", $System);
    $row = $sth->fetchrow_hashref();
    if (!defined($row)) {
	$sth->finish();
	return;
    }
    add("<p>");
    while ($row) {
	if (ExistsSelect("select key from artifacts, keys where artifacts.artifactid=keys.artifactid and donorid=? and key=? and turn=?;", $Donor->{donorid}, $row->{key}, $Turn)) {
	    add("<font color=\"#008000\">Stargate to <a href=\"system.cgi?" . UncanonicalizeSystem($row->{system2}) . "\">$row->{system2}</a>, requires key $row->{key}</font><br>\n");
	} else {
	    add("Stargate to <a href=\"system.cgi?" . UncanonicalizeSystem($row->{system2}) . "\">$row->{system2}</a>, requires key $row->{key}<br>\n");
	}
	$row = $sth->fetchrow_hashref();
    }
    $sth->finish();
}
	    
sub DoJumpCost {
    my($shipsystem, $cost);

    $shipsystem = GetLatestShipLocation($Donor->{ship});
    add("Cost to jump from $shipsystem to $System: ");
    $cost = GetJumpCost($Donor->{donorid}, $Turn, $shipsystem, $System);
    add("\$" . $cost);
}
    



sub DoStarnet {
    # Does it have a starnet?
    if (!ExistsSelect("select terminal from sysstarnet where system=?;", $System)) {
	return;
    }
    if (ExistsSelect("select turn from terminals where donorid=? and system=? and turn=?;",
		     $Donor->{donorid}, $System, $Turn)) {
	add("<p>Accessed Starnet Terminal\n");
    } else {
	add("<p><font color=\"#008000\">Unaccessed Starnet Terminal</font>\n");
    }
} # DoStarnet

sub DoPlague {
    my($row, $sth, $str);
    $sth = mydo("select * from sysplagues where system=?;", $System);
    $row = $sth->fetchrow_hashref();
    $sth->finish();
    if (!defined($row) || !exists($row->{system})) {
	return;
    }
    if (ExistsSelect("select turn from plagues where donorid=? and system=? and turn=?;",
		     $Donor->{donorid}, $System, $Turn)) {
	$str = "<p>Cured Plague";
    } else {
	$str = "<p><font color=\"#008000\">Uncured Plague</font>";
    }
    if (exists($row->{level}) && defined($row->{level}) &&
	exists($row->{turn}) && defined($row->{turn})) {
	$str .= " (reported at $row->{level}% on turn $row->{turn})";
    }
    add("$str\n");
} # DoPlague

sub DoCriminals {
    my($row, $sth);
    $sth = mydo("select * from criminals where system=? and turn=?;", $System, $Turn);
    $row = $sth->fetchrow_hashref();
    if (!defined($row)) {
	$sth->finish();
	return;
    }
    add("<p>");
    while ($row) {
	add("Criminal $row->{who} $row->{level} at $row->{location}<br>\n");
	$row = $sth->fetchrow_hashref();
    }
    $sth->finish();
    add("&nbsp;(Please see the notes on the <a href=\"criminals.cgi\">criminals</a> page for important information about criminals.)<br>\n");
}

sub DoRogues {
    my($row, $sth, %skill, $rstr);
    $sth = mydo("select * from rogues where system=? and turn=?;", $System, $Turn);
    $row = $sth->fetchrow_hashref();
    if (!defined($row)) {
	$sth->finish();
	return;
    }
    $skill{'Life Support'} = SelectOne("select lifesupportpercent from shipdata where donorid=? and turn=?;", $Donor->{donorid}, $Turn);
    $skill{'Impulse'} = SelectOne("select impulsepercent from shipdata where donorid=? and turn=?;", $Donor->{donorid}, $Turn);

    add("<p>");
    while ($row) {
	$rstr = "$row->{field} <a href=\"alien.cgi?$row->{race}\">$row->{race}</a> Rogue Band, requires $row->{danger}% $row->{location}";
	if (ExistsSelect("select who from enemies where donorid=? and who=? and turn=?;", $Donor->{donorid}, $row->{race}, $Turn)) {
	    $rstr .= " (you are enemies with the <a href=\"alien.cgi?$row->{race}\">$row->{race}</a> people)";
	} else {
	    $rstr .= " (you are not enemies with the <a href=\"alien.cgi?$row->{race}\">$row->{race}</a> people)";
	}
	    
	if ($row->{danger} <= $skill{$row->{location}}) {
	    add("<font color=\"#008000\">$rstr</font><br>\n");
	} else {
	    add("$rstr<br>\n");
	}
	$row = $sth->fetchrow_hashref();
    }
}

sub DoTradeData {
    my($turn, $sth, $row, $carry);

    $sth = mydo("select * from factories where system=?;", $System);
    $row = $sth->fetchrow_hashref();
    $sth->finish();
    $turn = GetLatestTurnFor('trade');

    if (defined($row) || $turn) {
	add("<hr>");
    }
    
    if (defined($row)) {
	add("Factory produces <a href=\"res.cgi?$row->{resource}\">$row->{resource}</a> for \$$row->{cost}<p>");
    }
    
    if ($turn) {
	add("Trade data last updated on turn $turn.&nbsp;&nbsp;&nbsp;");
	add("<a href=\"colonies.cgi?" . UncanonicalizeSystem($System) . "\"><font size=\"-1\">Colony Details</font></a>\n");
	add("<table>\n");
	add("<tr><th align=\"left\">Resource</th><th align=\"right\">&nbsp;&nbsp;Price</th><th align=right> &nbsp; Carrying</th></tr>\n");

	$sth = mydo("select t.resource, t.price, f.cost from trade t, factories f where t.system=? and turn=? and f.resource=t.resource;", 
		    $System, $turn);
	while ($row = $sth->fetchrow_hashref()) {
	    # Check if carrying it
	    $carry = SelectOne("select sum(n) from pods where donorid=? and turn=? and resource=?;", $Donor->{donorid}, $Turn, $row->{resource});
	    if (!defined($carry)) {
		$carry = 0;
	    }
	
	    add("<tr><td><a href=\"res.cgi?$row->{resource}\">$row->{resource}</a></td>");
	    add("<td align=\"right\">");
	    
	    if ($row->{price} <= $row->{cost} * 1.01) {
		add("<font color=\"#aa0000\">$row->{price}</font>");
	    } elsif ($row->{price} >= $row->{cost} * 2.5) {
		add("<font color=\"#008800\" size=\"+1\">$row->{price}</font>");
	    } elsif ($row->{price} >= $row->{cost} * 2) {
		add("<font color=\"#008800\">$row->{price}</font>");
	    } else {
		add("$row->{price}");
	    }
	    
	    add("</td>");

	    if ($carry > 0) {
		add("<td align=\"right\"><font color=\"#008800\">$carry</font></td></tr>\n");
	    } else {
		add("<td align=\"right\">$carry</td></tr>\n");
	    }
	}
	$sth->finish();
	add("</table>\n");
    }
    $turn = SelectOne("select max(turn) from turnupdate;");
    $sth = mydo("select * from medicine where ship=? and turn=?;", $Donor->{ship}, $turn);
    $row = $sth->fetchrow_hashref();
    if (defined($row) && exists($row->{system}) && defined($row->{system})) {
	add("<p>");
	if ($row->{system} eq $System) {
	    add("<font color=\"#008000\">");
	}
	add("Holding Medicine worth \$$row->{value} at <a href=\"system.cgi?" .
	    UncanonicalizeSystem($row->{system}) . "\">$row->{system}</a>\n");
	if ($row->{system} eq $System) {
	    add("</font>");
	}
    }
    $sth->finish();

} # DoTradeData

sub DoShopData {
    my($turn, $sth, $row, $yield, $reliability, $price, $tech);

    # Try to get shop data.
    $turn = GetLatestTurnFor('shop');
    
    if ($turn) {
	add("<hr><p>Shop data last updated on turn $turn.\n");
	add("<table>\n");
	add("<tr>\n");
	add("<th align=\"left\">Module</th>");
	add("<th align=\"left\">Tech Level&nbsp;&nbsp;&nbsp;</th>");
	add("<th align=\"left\">Energy<br>Yield</th>");
	add("<th align=\"right\">&nbsp;&nbsp;Reliability</th>");
	add("<th align=\"right\">&nbsp;&nbsp;&nbsp;Price</th>");
	add("</tr>\n");

	$sth = mydo("select * from shop where system=? and turn=? order by tech, type;", $System, $turn);
	while ($row = $sth->fetchrow_hashref()) {
	    $yield = getelem($row, 'yield');
	    $reliability = getelem($row, 'reliability');
	    if ($Donor->{secreturl} =~ m|^http://tbg.fyndo.com/tbg/share_[A-Z][a-z]*.htm$|) {
		$price = '';
	    } else {
		$price = getelem($row, 'price');
	    }
	    $tech = $TechLevels[$row->{tech}-1];
	    add("<tr>\n");
	    add("<td>$row->{item}&nbsp;&nbsp;&nbsp;</td>");
	    add("<td>$tech&nbsp;&nbsp;&nbsp;</td>");
	    add("<td align=\"left\">$yield</td>");
	    add("<td align=\"right\">&nbsp;&nbsp;&nbsp;$reliability</td>");
	    add("<td align=\"right\">&nbsp;&nbsp;&nbsp;$price</td>");
	    add("</tr>\n");
	}
	add("</table>\n");
	$sth->finish();
    }
} # DoShopData

sub DoAdventures {
    my($asth, $arow, $sdsth, $sdrow, %shiplevel);
    my($cando, $alreadycompleted, $isgood, $turn, $namestr);

    $turn = GetLatestTurnFor('adventures');
    if (!defined($turn) || $turn == 0 || $turn != $Turn) {
	return;
    }
    
    add("<hr>Adventures updated on turn $turn.\n");

    # get the ship levels
    $sdsth = mydo("select * from shipdata where donorid=? and turn=(select max(turn) from shipdata where donorid=?);", $Donor->{donorid}, $Donor->{donorid});
    $sdrow = $sdsth->fetchrow_hashref();
    if (!defined($sdrow)) {
	herror("Couldn't get ship data for $Donor->{ship}");
    }
    $sdsth->finish();
    $shiplevel{'Engineering'} = $sdrow->{engskill};
    $shiplevel{'Science'} = $sdrow->{sciskill};
    $shiplevel{'Medical'} = $sdrow->{medskill};
    $shiplevel{'Weaponry'} = $sdrow->{weapskill};
    
    $asth = mydo("select * from adventures where system=? and turn=? order by area, level, name;", 
		 $System, $turn);
    add("<table>\n");
    add("<tr><th align=left>Area-Level &nbsp; &nbsp; </th><th align=left>Name</th><th align=left>Sensor &nbsp; </th><th align=left>Can Do? &nbsp; </th><th>Completed?</th></tr>\n");
    while ($arow = $asth->fetchrow_hashref()) {
	if ($arow->{adv_all} && $Donor->{adv_all} ||
	    $arow->{adv_newbie} && $Donor->{adv_newbie} ||
	    $arow->{adv_done} && $Donor->{adv_done} ||
	    $arow->{adv_high} && $Donor->{adv_high} ||
	    $arow->{adv_hard} && $Donor->{adv_hard}) {

	    if ($arow->{level} <= $shiplevel{$arow->{area}}) {
		$cando = 1;
	    } else {
		$cando = 0;
	    }
	    if (CheckForSkill($Donor->{donorid}, $arow->{area}, $arow->{name})) {
		$alreadycompleted = 1;
	    } else {
		$alreadycompleted = 0;
	    }
	    add("<tr>\n");
	    $namestr = "<a href=\"http://lxs.sdf-eu.org/tbg/advcalc.cgi?level=$arow->{level}&usewp=1&wskill=$sdrow->{weapskill}&usemd=1&mskill=$sdrow->{medskill}#rg\">$arow->{name}</a>";
	    $isgood = $cando && !$alreadycompleted;
#	    if (defined($arow->{locid})) {
#		addelem("$arow->{locid}", $isgood);
#	    } else {
#		addelem("&nbsp;");
#	    }
	    addelem("$arow->{area}-$arow->{level}", $isgood);
	    addelem("$namestr &nbsp; ", $isgood);
	    if (defined($arow->{sensors})) {
		addelem("$arow->{sensors}%", $isgood);
	    } else {
		addelem("&nbsp;");
	    }
	    if ($cando) {
		addelem("Yes", $isgood);
	    } else {
		addelem("No", $isgood);
	    }
	    if ($alreadycompleted) {
		addelem("Yes", $isgood);
	    } else {
		addelem("No", $isgood);
	    }
	    add("</tr>\n");
	}
    }
    $asth->finish();
    add("</table>\n");
}  # DoAdventures

sub addelem {
    my($str, $cando) = @_;
    if (defined($cando) && $cando) {
	add("<td><font color=\"#008000\">$str</font></td>");
    } else {
	add("<td>$str</td>");
    }
}

sub GetLatestTurnFor {
    my($table) = @_;
    my($sth, $row, $turn);

    $sth = mydo("select max(turn) from $table where system=?;", $System);
    $row = $sth->fetchrow_hashref();
    if (defined($row) && exists($row->{max}) && defined($row->{max}) &&
	$row->{max} =~ /^[0-9]+$/) {
	$turn = $row->{max};
    } else {
	$turn = 0;
    }
    $sth->finish();
    return $turn;
}

sub getelem {
    my($row, $elem) = @_;
    if (exists($row->{$elem}) && defined($row->{$elem})) {
	return $row->{$elem};
    } else {
	return "&nbsp;";
    }
}
