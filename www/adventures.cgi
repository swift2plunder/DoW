#!/usr/bin/perl -w
#
# Show adventures info.
#

use strict;
use Getopt::Std;

use dow;

use vars qw($opt_s);

my ($Orderby, $Donor, $DonorID);

$Donor = ProcessDowCommandline();

getopts('s:') or usage();

if ($#ARGV != -1) {
    usage();
}

$DonorID = $Donor->{donorid};

if (!defined($opt_s) || $opt_s =~ /^\s*$/) {
    $opt_s = SelectOne("select advsort from prefs where donorid=?;", $DonorID);
}

$Orderby = GenerateOrderBy($opt_s, ('s' => 'system',
				    'e' => 'sensors',
				    'a' => 'area',
				    'l' => 'level',
				    'n' => 'name'));

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: adventures.cgi?-s+saln\n<br> &nbsp; -s   Sort order\n<br>");
}

sub GeneratePage {
    my($ship, %shiplevel, %ncrew, $sdrow, $sdsth, $turn);
    my($asth, $arow, $cando, $alreadycompleted, $linkname);
    my($sa, $psth, $prefs);

    $ship = $Donor->{ship};
    $turn = SelectOne("select max(turn) from turnupdate where donorid=?;",
		      $DonorID);

    add(DOW_HTML_Header($Donor, "DOW Adventures for $ship"));
    add("<h1>DOW Adventures for \"$ship\"</h1>\n");
    add("<p>You will only see adventures if you offer the same information as the person who donated the adventure. If you want more adventures, offer more. To see what you're currently offering, go to your <a href=\"ms.cgi\">membership</a> page.\n");
    add("<p>Click on the column heading to sort by that column.");
    add("<p>Click on the adventure name to access risk information and crew requirements (courtesy of Belle Epoque). It assumes both Medical and Weaponry Officer participate in the adventure.  Deselect the checkboxes on the linked page and resubmit to see the risks if they don't go.");
    add("<p>Go to <a href=\"advmap.cgi\">Map View</a>.<p>");
    
    $psth = mydo("select * from prefs where donorid=?;", $DonorID);
    $prefs = $psth->fetchrow_hashref();
    if (!defined($prefs)) {
	herror("Couldn't find preferences for ship $ship");
    }

    # get the ship levels
    $sdsth = mydo("select * from shipdata where donorid=? and turn=?;",
		  $DonorID, $turn);
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
    
    $asth = mydo("select * from adventures where turn=? $Orderby;", $turn);
    
    add("<table border>\n<tr>");

    $sa = GenerateSortArg($opt_s, 's');
    add("<th><a href=\"adventures.cgi?-s+$sa\">System</a></th>\n");
    add("<th>Jump Cost</th>\n");
    $sa = GenerateSortArg($opt_s, 'a');
    add("<th><a href=\"adventures.cgi?-s+$sa\">Area</a>");
    $sa = GenerateSortArg($opt_s, 'l');
    add("-<a href=\"adventures.cgi?-s+$sa\">Level</a></th>\n");
    add("<th>Crew</th>\n");
    $sa = GenerateSortArg($opt_s, 'n');
    add("<th><a href=\"adventures.cgi?-s+$sa\">Name</a></th>\n");
    $sa = GenerateSortArg($opt_s, 'e');
    add("<th><a href=\"adventures.cgi?-s+$sa\">Sensors</a></th>\n");
    if ($prefs->{advhard}) {
	add("<th>Can Do?</th>");
    }
    if ($prefs->{advdone}) {
	add("<th>Completed?</th>");
    }
    add("</tr>\n");

    while ($arow = $asth->fetchrow_hashref()) {
	if ($arow->{adv_all} && $Donor->{adv_all} ||
	    $arow->{adv_newbie} && $Donor->{adv_newbie} ||
	    $arow->{adv_done} && $Donor->{adv_done} ||
	    $arow->{adv_high} && $Donor->{adv_high} ||
	    $arow->{adv_hard} && $Donor->{adv_hard}) {

	    if ($arow->{level} <= $shiplevel{$arow->{area}} &&
		int($arow->{level}/2) <= $ncrew{$arow->{area}}) {
		$cando = 1;
	    } else {
		$cando = 0;
	    }
	    if (CheckForSkill($DonorID, $arow->{area}, $arow->{name})) {
		$alreadycompleted = 1;
	    } else {
		$alreadycompleted = 0;
	    }
	    if (($cando || $prefs->{advhard}) && (!$alreadycompleted || $prefs->{advdone})) {
		add("<tr>\n");
		$linkname = UncanonicalizeSystem($arow->{system});
		addelem("<a href=\"system.cgi?$linkname\">$arow->{system}</a>");
		addelem(GetJumpCost($DonorID, $turn, $arow->{system}, 
				    SelectOne("select system from shiploc where ship=? and turn=?;", $Donor->{ship}, $turn)));
		addelem("$arow->{area}-$arow->{level}");
		addelem(int($arow->{level}/2));
		addelem("<a href=\"http://lxs.sdf-eu.org/tbg/advcalc.cgi?level=$arow->{level}&usewp=1&wskill=$sdrow->{weapskill}&usemd=1&mskill=$sdrow->{medskill}#rg\">$arow->{name}</a>");
		if (defined($arow->{sensors})) {
		    addelem("$arow->{sensors}%");
		} else {
		    addelem("&nbsp;");
		}
		if ($prefs->{advhard}) {
		    if ($cando) {
			addelem("Yes", "#008000");
		    } else {
			addelem("No");
		    }
		}
		if ($prefs->{advdone}) {
		    if ($alreadycompleted) {
			addelem("Yes");
		    } else {
			addelem("No", "#008000");
		    }
		}
		add("</tr>");
	    }
	}
    }
    $asth->finish();
    add("</table>\n");
    add("<form method=post action=\"advprefssubmit.cgi\">\n");
    add("<input name=donorid type=hidden value=\"$DonorID\">\n");
    add("<input name=returnto type=hidden value=\"adventures.cgi\">\n");
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
    add("<tr><td><input type=checkbox name=advsort value=$opt_s></td>");
    add("<td>Make this sort order the default ($opt_s).</td></tr>");
    add("</table>\n<p><input type=submit> &nbsp; <input type=reset>\n</form>\n");
    add(DOW_HTML_Footer($Donor));
}

sub addelem {
    my($str, $color) = @_;
    if (defined($color)) {
	add("<td><font color=\"$color\">$str</font></td>");
    } else {
	add("<td>$str</td>");
    }
}
