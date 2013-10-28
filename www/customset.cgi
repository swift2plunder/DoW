#!/usr/bin/perl -w
#
# Custom Set
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
    herror("Usage: customset.cgi");
}

sub GeneratePage {
    my($turn);
    $turn = SelectOne("select max(turn) from turnupdate where donorid=?;",
		      $Donor->{donorid});
    add(DOW_HTML_Header($Donor, "DOW - Custom Set"));
    add("<h1>DOW - Custom Set</h1>\n");
    add("<p>For each system, if the specified item exists in the system, the score is added to a running sum. When you hit submit, you'll see a list of all systems with score greater than 0 in order. Positive and negative integers may be used. Items with an asterisk (*) are not yet implemented.\n");
    add("<p><em>Jump Cost</em> and <em>Value of Resources</em> work a bit differently. The weight you enter is multiplied by the actual cost (or value), and the product is added to the score for the system.");
    add("<p>I suggest setting <em>Jump Cost</em> to -1, <em>Value of Resources</em> to 1, and the others to the cash value you assign to each category.");
    add("<p><hr><p><form method=post action=\"customsetsubmit.cgi\">\n");
    add("<input name=dow_pw type=hidden value=\"$Donor->{dow_pw}\">\n");
    add("<input name=turn type=hidden value=$turn>\n");

    add("<table>\n");
    addline("Jump Cost", "jumpcost");
    addline("Value of Resources at destination", "resources");
    add("<tr><td colspan=2><input type=checkbox name=useorders value=true");
    if (ExistsSelect("select * from customsetprefs where donorid=?;", $Donor->{donorid}) &&
	SelectOne("select useorders from customsetprefs where donorid=?", $Donor->{donorid})) {
	add(" checked");
    }
    add("> Download and apply buy/sell orders to trade resources</td></tr>\n");

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
    addcomboline("Preferred Adventures (level " . 
		 SelectOne("select prefadvmin from prefs where donorid=?;",
			   $Donor->{donorid}) . "-" .
		 SelectOne("select prefadvmax from prefs where donorid=?;",
			   $Donor->{donorid}) . ")",
		 "padv");
    add("<tr><td colspan=5><font size=\"-1\">Go to <a href=\"prefs.cgi\">View Preferences</a> to change Preferred Adventure levels</font></td></tr>\n");
    addcomboline("Academy", "acad");
    addcomboline("School", "school");
    addcomboline("Rogue Band", "rogue");
    add("</table>\n");
    add("<p><input type=checkbox name=default value=true checked> Use as default");
    add(" &nbsp; &nbsp; <input type=checkbox name=mapview value=true> Map View");
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
    $sth = mydo("select $str from customsetprefs where donorid=?;", $Donor->{donorid});
    $row = $sth->fetchrow_hashref();
    if (defined($row) && exists($row->{$str}) && defined($row->{$str}) &&
	$row->{$str} =~ /^\s*-?[0-9]+\s*$/) {
	$val = $row->{$str};
    } else {
	$val = 0;
    }
    add("<td><input type=text name=$str value=\"$val\" size=10></td>");
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
