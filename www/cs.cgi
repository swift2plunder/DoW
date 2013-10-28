#!/usr/bin/perl -w
#
# Combat simulator - select ships
#

use strict;
use dow;

my $Donor = ProcessDowCommandline();
my $Turn = SelectOne("select max(turn) from turnupdate;");

if (! $Donor->{shipconfig}) {
    herror("The combat simulator requires ship configurations. Therefore, you must donate ship configurations to run the simulator.");
}

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: cs.cgi");
}

sub GeneratePage {
    add(DOW_HTML_Header($Donor, "Combat Simulator"));
    add("<h1>Combat Simulator</h1>\n");
    add("<p><blink>Warning!</blink> The combat simulator has not been updated to any of the new combat rules. Use with caution!\n");

    add("<p>You may only run the combat simulator under the following conditions:\n");
    add("<ol><li>Simulating combat of you vs. a banned ship");
    add("<li>You volunteer with the <a href=\"xeno.cgi\">Institute of Xenology</a> and you are simulating you vs. the ship you are paired with\n");
    add("</ol><p>");

    # Everyone gets to simulate vs. banned.
    DoBanned();
    
    # Xeno vs. paired
    if ($Donor->{xeno}) {
	DoPaired();
    }
    
    add(DOW_HTML_Footer($Donor));
}

sub DoBanned {
    add("<p><hr><p><em>$Donor->{ship} vs.</em>\n");
    add("<table>\n");
    foreach my $bannedship (SelectAll("select b.ship from banned b, activeships a where a.turn=$Turn and b.ship=a.ship;")) {
	add("<tr><td><a href=\"shipsummary.cgi?$bannedship\">$bannedship</a> &nbsp; &nbsp; </td>\n");
	addbanline('Asteroids', $bannedship);
	addbanline('Clear', $bannedship);
	addbanline('Dyson Sphere', $bannedship);
	addbanline('Nebula', $bannedship);
	add("</tr>\n");
    }
    add("</table>");
}

sub addbanline {
    my($str, $bannedship) = @_;
    add("<td><a href=\"combat_options.cgi?ship1=$Donor->{ship}&ship2=$bannedship&terrain=$str\">$str</a> &nbsp; &nbsp;</td>\n");
}


sub DoPaired {
    my($pship, $terrain, $homeworld, $race, $system);

    $terrain = SelectOne("select terrain from terrain, shiploc where terrain.system=shiploc.system and turn=? and ship=?;", $Turn, $Donor->{ship});
    $pship = PairedShip($Donor->{ship}, $Turn);
    $race = RaceOfShip($pship);
    $system = SelectOne("select system from shiploc where ship=? and turn=?;", 
			$Donor->{ship}, $Turn);
    if (defined($race) && ExistsSelect("select * from aliens where race=? and system=?;", 
				       $race, $system)) {
	$homeworld = 1;
    } else {
	$homeworld = 0;
    }
    
    add("<p><hr><p><a href=\"combat_options.cgi?ship1=$Donor->{ship}&ship2=$pship&terrain=$terrain&homeworld=$homeworld\">$Donor->{ship} vs. $pship</a>");
}

sub DoAll {
    add("<p><hr><p><form method=post action=\"combat_options.cgi\">\n");
    add("<table><tr><td valign=top><table><tr>");
    add("<td>Ship 1:</td><td><input type=text size=50 name=ship1></td></tr>\n");
    add("<td>Ship 2:</td><td><input type=text size=50 name=ship2></td></tr></table></td>");
    add("<td>");
    add("<select size=4 name=terrain>");
    add("<option selected>Clear</option>");
    add("<option>Asteroid</option>");
    add("<option>Nebula</option>");
    add("<option>Dyson Sphere</option>");
    add("</select>");
    add("</td></tr></table>");
    add("<p><input type=submit> &nbsp; <input type=reset>\n");
    add("</form>");
}
