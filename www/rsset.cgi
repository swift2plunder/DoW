#!/usr/bin/perl -w
#
# Set route simulator settings.
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
    herror("Usage: rsset.cgi");
}

sub GeneratePage {
    my($sth, $row, $excludepods);
    add(DOW_HTML_Header($Donor, "DOW - Route Simulator Settings"));
    add("<h1>DOW - Route Simulator Settings</h1>\n");
    add("<p>See my <a href=\"http://janin.org/ninja/tradesim.html\">route simulator</a> page for a description of the route simulator.");
    add("<p>Because the route simulator is so computationally expensive, I am limiting its use to members of the Institute of Xenology (<a href=\"xeno.cgi\">Xenos</a>).");
    add(" Also, it does not run interactively. You just change the settings here. The simulator will run automatically twice a day if you've submitted the form here. To see the results, go to <a href=\"rsresults.cgi\">Route Simulator Results</a>.");    
    add("<p><hr><p><form method=post action=\"rssetsubmit.cgi\">\n");
    add("<input name=dow_pw type=hidden value=\"$Donor->{dow_pw}\">\n");
    add("<hr><table>\n");
    addboolline('Do you trade in contrband?', 'contraband');
    addboolline('Include jumps to Olympus?', 'olympian');
    addline("Number of turns to simulate?", 'nturns');
    addline("Maximum cost of single jump?", 'maxjump');
    addline("Maximum to spend on resources in one turn?", 'maxpurchase');
    addline("Start energy multiplier?", 'energypercent');
    addline("Cargo value multiplier?", 'cargoweight');
    add("</table><hr>\n");
    add("<p>Number of turns should be 2 to 6. For no limit to cost of a single jump, use -1. Using a value other than -1 will speed up the simulator and save memory.\n");
    add("<p>Use -1 for \"Maximum to spend on resources in one turn\" for no limit. Otherwise, the simulator will never purchase more than this amount worth of resources on any one turn.\n");
    add("<p>The start energy multiplier should be between 0.0 and 1.0. Your current energy (money) on hand is multiplied by this factor before being passed to the simulator. Set it under 1.0 to establish a reserve fund.\n");
    add("<p>Cargo value multiplier should be 1.0 to make cargo you're carrying equal in value to the cost to buy the cargo, up to about 3.0 to make cargo you're carrying worth 3 times as much as the purchase price. 1.5 is a good compromise.\n");
    add("<p>The following settings are very similar to the <a href=\"customset.cgi\">Custom</a> feature, except that jump costs are fixed at -1 and resource values are fixed at 1.");
    add(" For each system, if the specified item exists in the system, the score is added to a running sum. Positive and negative integers may be used. You can think of the score as the value (in energy) of jumping to a system with the associated attribute.\n");
    add("<p>The way the Route Simulator works is to precompute the bonus value once for each system based on the settings you enter below. The bonus is added to the route only once, so staying multiple turns at the same system does not accumulate score. I plan to add recurring vs. non-recurring bonuses at some point.");

    add("<p><hr><table>\n");
    addline("Starnet Terminal", "sn");
    addline("Unaccessed Terminal", "usn");
    addline("Alien Homeworld", "hw");
    addline("Alien Homeworld with Uncured Plague", "hwup");
    addline("Alien Homeworld of a Non-Enemy", "hwne");
    addline("Hostile Alien Homeworld", "hwh");
    addline("Chaotic Alien Homeworld", "hwc");
    addline("Factory", "factory");
    addline("Contraband Factory", "cfactory");
    addline("Hiring Hall", "hiringhall");
    addline("Prison", "prison");
    addline("Ocean", "ocean");
    addline("Out of Date", "ood");
    add("</table>\n<p>\n");
    add("<table>\n");
    add("<tr><th>&nbsp;</th><th>Engineering</th><th>Science</th><th>Medical</th><th>Weaponry</th></tr>\n");
    addcomboline("Adventure", "adv");
    addcomboline("Uncompleted Adventure", "uadv");
    addcomboline("Academy", "acad");
    addcomboline("School", "school");
    addcomboline("Rogue Band", "rogue");
    add("</table>\n<hr>\n");
    add("<p>Below, you can enter additional bonuses by hand. The format must be <em>exactly</em> correct. It should be a comma seperated list of \"system name\" followed by bonus. For example, <em>Star \#3 &nbsp;100, Alcor &nbsp;300, Olympus &nbsp;-10, Star \#5 &nbsp;-200</em>. Notice, no comma between the system name and the bonus.\n<p>");
    addinput("system_bonuses", 100);
    add("<p><hr><p>Select pods from the form below to <em>exclude</em> them from being loaded or unloaded by the simulator.<br>\n");
    $sth = mydo("select * from pods where donorid=? and turn=?;", 
		$Donor->{donorid}, SelectOne("select max(turn) from turnupdate;"));
    if (ExistsSelect("select * from rss where donorid=?;", $Donor->{donorid})) {
	$excludepods = SelectOne("select excludepods from rss where donorid=?;",
				 $Donor->{donorid});
    } else {
	$excludepods = "";
    }
    # add("debug: $excludepods\n<p>");
    add("<select size=6 name=excludepods multiple>\n");
    while ($row = $sth->fetchrow_hashref()) {
	add("<option value=\"$row->{name}\"");
	if (index($excludepods, $row->{name}) != -1) {
	    add(" selected");
	}
	add(">$row->{name} $row->{n}/$row->{capacity}");
	if (exists($row->{resource}) && $row->{resource} !~ /^\s*$/) {
	    add(" $row->{resource}");
	}
	add("</option>\n");
    }
    add("</select>\n");
    $sth->finish();
    add("<p><hr>\n");
    add("<p><input type=submit> &nbsp; <input type=reset>\n");
    add("</form>\n");
    add(DOW_HTML_Footer($Donor));
}

sub addline {
    my ($lab, $str) = @_;
    add("<tr><td>$lab</td>");
    addelem($str);
    add("</tr>\n");
}

sub addelem {
    my($str) = @_;
    my($val, $sth, $row);
    $sth = mydo("select $str from rss where donorid=?;", $Donor->{donorid});
    $row = $sth->fetchrow_hashref();
    if (defined($row) && exists($row->{$str}) && defined($row->{$str}) &&
	$row->{$str} =~ /^\s*-?[0-9.]+\s*$/) {
	$val = $row->{$str};
    } else {
	$val = 0;
    }
    $sth->finish();
    add("<td><input type=text name=$str value=\"$val\" size=10></td>");
}

sub addinput {
    my($str, $size) = @_;
    my($sth, $row);
    add("<input type=text name=$str size=$size");
    $sth = mydo("select $str from rss where donorid=?;", 
		$Donor->{donorid});
    $row = $sth->fetchrow_hashref();
    if (defined($row) && exists($row->{$str}) && defined($row->{$str}) &&
	$row->{$str} !~ /^\s*$/) {
	add(" value=\"$row->{$str}\"");
    }
    add(">");
}
	
sub addboolline {
    my($desc, $lab) = @_;
    my($selyes, $selno, $sth, $row);

    $sth = mydo("select $lab from rss where donorid=?;", $Donor->{donorid});
    $row = $sth->fetchrow_hashref();
    if (defined($row) && exists($row->{$lab}) && defined($row->{$lab}) &&
	$row->{$lab}) {
	$selyes = ' selected';
	$selno = '';
    } else {
	$selyes = '';
	$selno = ' selected';
    }
    $sth->finish();

    add("<tr><td>$desc</td>\n");
    add("<td><select name=$lab>");
    add("<option$selyes>Yes</option>\n");
    add("<option$selno>No</option></select></td>\n");
    add("</tr>\n");
}

sub addcomboline {
    my($lab, $str) = @_;
    my($c);
    add("<tr><td>$lab</td>");
    foreach $c (qw(e s m w)) {
	addelem($c . $str);
    }
    add("</tr>\n");
}
