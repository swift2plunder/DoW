#!/usr/bin/perl -w
#
# Set view preferences
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
    herror("Usage: prefs.cgi");
}

sub GeneratePage {
    my($prefs, $sth);

    $sth = mydo("select * from prefs where donorid=?;", $Donor->{donorid});
    $prefs = $sth->fetchrow_hashref();
    if (!defined($prefs)) {
	herror("Couldn't get prefs for $Donor->{ship}");
    }
    $sth->finish();
    
    add(DOW_HTML_Header($Donor, "DOW View Preferences for $Donor->{ship}"));
    add("<h1>DOW View Preferences for $Donor->{ship}</h1>\n");
    add("<form method=post action=\"prefssubmit.cgi\">\n");
    add("<input name=donorid type=hidden value=\"$Donor->{donorid}\">\n");
    add("<hr><h3>Navigation</h3>\n");
    add("The following html string is added to the bottom of every page. Please be careful! If you enter illegal html, it can prevent you from viewing.\n<p>");
    add("<input type=text size=100 name=bottombar value=\"" . QuoteHTML($prefs->{bottombar}) . "\">");
    add("\n<br>Example: " . QuoteHTML("<a href=\"http://janin.org/dow\">DOW</a> &nbsp; <a href=\"turnulator.cgi\">Orders</a>\n"));

#   add("<p><input type=checkbox name=showleftbar value=true");
#   if ($prefs->{showleftbar}) {
#	add(" checked");
#    }
#    add(">Show Left Navigation Bar\n");
    add("<p>Left Navigation Bar Width: <input type=text size=8 name=leftbarwidth value=\"" .
	$prefs->{leftbarwidth} . "\">");
    add("<hr><h3>Adventures</h3>\n");
    add("<table>\n");
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
    add("<tr><td><input type=checkbox name=onlyprefadv value=true");
    if ($prefs->{onlyprefadv}) {
	add(" checked");
    }
    add("></td><td>Show only preferred-level adventures</td></tr>");
    add("</table>");
    add("Preferred Adventure Level &nbsp; Min:");
    add("<input type=text name=prefadvmin size=4 value=\"$prefs->{prefadvmin}\">");
    add("&nbsp;&nbsp;&nbsp;Max:");
    add("<input type=text name=prefadvmax size=4 value=\"$prefs->{prefadvmax}\">\n");
    add("<p><input type=text name=advsort size=6 value=\"$prefs->{advsort}\">");
    add(" &nbsp; Default sort order. A string consisting of the letters s (system), l (level), a (area), n (name). Use caps to sort in reverse order. E.g. <em>aLsn</em>.\n");


    add("<hr><h3>Systems Page</h3>\n");
    add("<table>\n");
    add("<tr><td><input type=checkbox name=mapinsys value=true");
    if ($prefs->{mapinsys}) {
	add(" checked");
    }
    add("></td><td>Show map in system view.</td></tr>\n");
    add("</table>\n");
    
    add("<hr><input type=submit> &nbsp; <input type=reset>\n");
    add("</form>\n");
    add(DOW_HTML_Footer($Donor));
}
    
