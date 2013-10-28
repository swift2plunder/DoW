#!/usr/bin/perl -w
#
# Show adventures map.
#

use strict;

use dow;

my $Donor = ProcessDowCommandline();

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: advmap.cgi<br>\n");
}

sub GeneratePage {
    my($ship, $asth, $arow, %shiplevel, %ncrew, $sdrow, $sdsth);
    my($cando, $alreadycompleted, $psth, $prefs);
    my(%area, %sensors, %syshtml, $turn, $sys);

    $turn = SelectOne("select max(turn) from turnupdate;");
    $ship = $Donor->{ship};

    add(DOW_HTML_Header($Donor, "DOW Adventures for $ship"));
    add("<h1>DOW Adventures for \"$ship\"</h1>\n");
    add("<p>You will only see adventures if you offer the same information as the person who donated the adventure. If you want more adventures, offer more. To see what you're currently offering, go to your <a href=\"ms.cgi\">membership</a> page.\n");
    add("<p>Go to <a href=\"adventures.cgi\">List View</a>.\n");

    add("<hr>");

        
    # get the ship levels
    $sdsth = mydo("select * from shipdata where donorid=? and turn=?;", $Donor->{donorid}, $turn);
    $sdrow = $sdsth->fetchrow_hashref();
    if (!defined($sdrow)) {
	herror("Couldn't get ship data for $ship");
    }
    $shiplevel{'Engineering'} = $sdrow->{engskill};
    $shiplevel{'Science'} = $sdrow->{sciskill};
    $shiplevel{'Medical'} = $sdrow->{medskill};
    $shiplevel{'Weaponry'} = $sdrow->{weapskill};

    $ncrew{'Engineering'} = $sdrow->{nengcrew};
    $ncrew{'Science'} = $sdrow->{nscicrew};
    $ncrew{'Medical'} = $sdrow->{nmedcrew};
    $ncrew{'Weaponry'} = $sdrow->{nweapcrew};

    $psth = mydo("select * from prefs where donorid=?;", $Donor->{donorid});
    $prefs = $psth->fetchrow_hashref();
    if (!defined($prefs)) {
	herror("Couldn't find preferences for ship $ship");
    }

    $asth = mydo("select * from adventures where turn=?;", $turn);
    
    if ($prefs->{onlyprefadv}) {
	add("Showing only preferred adventures (level $prefs->{prefadvmin}-$prefs->{prefadvmax}). To show all adventures or change preferred levels, go to");
    } else {
	add("Showing all adventure levels. To show only preferred levels, go to");
    }
    add(" <a href=\"prefs.cgi\">Preferences</a>.\n");

    while ($arow = $asth->fetchrow_hashref()) {
	if (($arow->{adv_all} && $Donor->{adv_all} ||
	     $arow->{adv_newbie} && $Donor->{adv_newbie} ||
	     $arow->{adv_done} && $Donor->{adv_done} ||
	     $arow->{adv_high} && $Donor->{adv_high} ||
	     $arow->{adv_hard} && $Donor->{adv_hard}) &&
	    (!$prefs->{onlyprefadv} || 
	     ($prefs->{prefadvmin} <= $arow->{level} && $arow->{level} <= $prefs->{prefadvmax}))) {

	    if ($arow->{level} <= $shiplevel{$arow->{area}} &&
		int($arow->{level}/2) <= $ncrew{$arow->{area}}) {
		$cando = 1;
	    } else {
		$cando = 0;
	    }
	    if (CheckForSkill($Donor->{donorid}, $arow->{area}, $arow->{name})) {
		$alreadycompleted = 1;
	    } else {
		$alreadycompleted = 0;
	    }
	    if (($cando || $prefs->{advhard}) && 
		(!$alreadycompleted || $prefs->{advdone})) {
		if (!exists($area{$arow->{system}})) {
		    $area{$arow->{system}} = "";
		}
		$area{$arow->{system}} .= lc(substr($arow->{area}, 0, 1));
		if (exists($arow->{sensors}) && defined($arow->{sensors}) &&
		    $arow->{sensors} <= $sdrow->{sensorpercent}) {
		    if (!exists($sensors{$arow->{system}})) {
			$sensors{$arow->{system}} = "";
		    }
		    $sensors{$arow->{system}} .= lc(substr($arow->{area}, 0, 1));
		}
	    }
	}
    }
    $asth->finish();
    foreach $sys (keys %area) {
	$syshtml{$sys} = "<img border=none src=\"cplanet.cgi?-n+13+-a+$area{$sys}";
	if (exists($sensors{$sys})) {
	    $syshtml{$sys} .= "+-s+$sensors{$sys}";
	}
	$syshtml{$sys} .= "\">";
    }
    add(MakeMapGeneralNew($ship, \%syshtml, "<img border=none src=\"smallgray.gif\">"));
    add("<p><hr><p>\n");
    add("<table><tr><td>\n");
    add("<table  border=0 cellspacing=0 cellpadding=0>\n");
    add("<tr><td align=right>Engineering</td><td></td><td>Science</td></tr>\n");
    add("<tr><td></td><td align=center><img src=\"cplanet.cgi?-n+23+-a+esmw\"></td><td></td></tr>\n");
    add("<tr><td align=right>Weaponry</td><td></td><td>Medical</td></tr>\n");
    add("</table>\n");
    add("</td><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td><td>");
    add("<table border=0 cellspacing=0 cellpadding=0>\n");
    add("<tr><td></td><td>Your sensors are lower than adventure cloak (or adventure cloak unknown)</td></tr>\n");
    add("<tr><td><img src=\"cplanet.cgi?-n+23+-a+sm+-s+m\"></td><td></td></tr>\n");
    add("<tr><td></td><td>Your sensors are higher than adventure cloak</td></tr>\n");
    add("</table>\n");

    add("</td></tr></table>\n");
    add("<p><hr><p>\n");
    add("<form method=post action=\"advprefssubmit.cgi\">\n");
    add("<input name=donorid type=hidden value=\"$Donor->{donorid}\">\n");
    add("<input name=returnto type=hidden value=\"advmap.cgi\">\n");
    add("<p><table>\n");
    add("<tr><td><input type=checkbox name=advdone value=true");
    if ($prefs->{advdone}) {
	add(" checked");
    }
    add("></td><td>Show adventures you've already completed.</td></tr>\n");

    add("<tr><td><input type=checkbox name=advhard value=true");
    if ($prefs->{advhard}) {
	add(" checked");
    }
    add("></td><td>Show adventures that are too high level or require too much crew for you to do.</td></tr>\n");
    add("</table>\n<p><input type=submit> &nbsp; <input type=reset>\n</form>\n");
    $sdsth->finish();	
    add(DOW_HTML_Footer($Donor));
}
