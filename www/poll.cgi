#!/usr/bin/perl -w
#
# With no arguments, list all polls (both open and historic).
# With one argument, show that poll.
#   If the poll is open, allow the user to vote (or change their vote)
#   If the poll is closed, show results.
#

use strict;
use Getopt::Std;

use dow;

my $Donor = ProcessDowCommandline();

if ($#ARGV == -1) {
    GeneratePollList();
} elsif ($#ARGV == 0) {
    GeneratePoll($ARGV[0]);
}

PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: poll.cgi[?PollID]");
}

sub GeneratePollList {
    my($sth, $row);
    add(DOW_HTML_Header($Donor, "DOW Polls"));
    add("<h1>DOW Polls</h1>\n");
    add("Discussion of the polls takes place on the <a href=\"forumread.cgi\">forums</a>.\n");
    add("<p><hr>\n");
    add("<h3>Open Polls:</h3>\n");
    $sth = mydo("select * from polls where open=true;");
    while ($row = $sth->fetchrow_hashref()) {
	add("<a href=\"poll.cgi?$row->{pollid}\">$row->{title}</a><br>\n");
    }
    $sth->finish();
    add("<p><hr>\n");
    add("<h3>Closed Polls:</h3>\n");
    $sth = mydo("select * from polls where open=false;");
    while ($row = $sth->fetchrow_hashref()) {
	add("<a href=\"poll.cgi?$row->{pollid}\">$row->{title}</a><br>\n");
    }
    $sth->finish();
    add("<p><hr>\n");
    add(DOW_HTML_Footer($Donor));
}


sub GeneratePoll {
    my($pollid) = @_;

    if (ExistsSelect("select * from polls where pollid=? and open=true;", $pollid)) {
	GenerateOpenPoll($pollid);
    } elsif (ExistsSelect("select * from polls where pollid=? and open=false;", $pollid)) {
	GenerateClosedPoll($pollid);
    } else {
	herror("Neither open nor closed. Shouldn't happen!");
    }
    add(DOW_HTML_Footer($Donor));
}

sub GenerateClosedPoll {
    my($pollid) = @_;
    my($sth, $row, $totalvotes, $nvotes);

    $totalvotes = SelectOne("select count(*) from pollvotes where pollid=?;", 
			    $pollid);
    add(DOW_HTML_Header($Donor, "DOW Poll"));
    add("<h1>Closed Poll.</h1>\n<p>");
    add("Discussion of the poll took place on either the (now defunct) Yahoo forums or on the DOW <a href=\"forumread.cgi\">forums</a>.<br><br><hr>\n");
    add(SelectOne("select title from polls where pollid=?;", $pollid));
    add("<p>");
    if (ExistsSelect("select note from polls where pollid=?;", $pollid)) {
	add(SelectOne("select note from polls where pollid=?;", $pollid));
	add("<p>\n");
    }

    $sth = mydo("select item from pollitems, pollvotes where donorid=? and pollitems.pollitemid=pollvotes.pollitemid and pollitems.pollid=?;", $Donor->{donorid}, $pollid);
    $row = $sth->fetchrow_hashref();
    if (defined($row) && exists($row->{item}) && defined($row->{item})) {
	add("&nbsp;&nbsp;&nbsp;Your vote: $row->{item}.<p>\n");
    } else {
	add("&nbsp;&nbsp;&nbsp;You did not vote in this poll.<p>\n");
    }
    $sth->finish();

    $sth = mydo("select * from pollitems where pollid=?;", $pollid);
    add("<table>\n");
    add("<tr><td colspan=3><hr></td></tr>\n");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr>\n");
	add(" <td>$row->{item}&nbsp;&nbsp;&nbsp;</td>\n");
	$nvotes = SelectOne("select count(*) from pollvotes where pollitemid=?;", $row->{pollitemid});
	add(" <td align=right>$nvotes</td>\n");
	if ($totalvotes > 0) {
	    add(sprintf(" <td align=right>%.1f%%</td>\n", 
			100.0*$nvotes/$totalvotes));
	} else {
	    add("<td align=right>?</td>\n");
	}
	add("</tr>\n");
    }
    $sth->finish();
    add("<tr><td colspan=3><hr></td></tr>\n");
    add("<tr><td><em>Total Votes&nbsp;&nbsp;</em></td><td align=right>$totalvotes</td><td align=right>&nbsp;&nbsp;&nbsp;&nbsp;100.0%</td></tr>\n");
    add("</table>");
}
    

sub GenerateOpenPoll {
    my($pollid) = @_;
    my($sth, $row, $close);
    add(DOW_HTML_Header($Donor, "DOW Poll"));
    add("Discussion of the poll takes place on <a href=\"forumread.cgi\">forums</a>.\n");
    add("<p>" . SelectOne("select title from polls where pollid=?;", $pollid) . "\n");
    if (ExistsSelect("select note from polls where pollid=?;", $pollid)) {
	add("<p>" . SelectOne("select note from polls where pollid=?;", $pollid));
	add("<p>\n");
    }

    add("<form method=post action=\"pollsubmit.cgi\">\n");
    add("<input name=dow_pw type=hidden value=\"$Donor->{dow_pw}\">\n");
    add("<input name=pollid type=hidden value=$pollid>\n");
    $sth = mydo("select * from pollitems where pollid=?;", $pollid);
    add("<table>\n");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr><td><input type=radio name=\"item\" value=\"$row->{pollitemid}\"");
	if (ExistsSelect("select * from pollvotes where donorid=? and pollitemid=?;",
			 $Donor->{donorid}, $row->{pollitemid})) {
	    add(" checked");
	}
	add("></td><td>$row->{item}</td></tr>\n");
    }
    $sth->finish();
    add("</table>\n<p>");
    add("<input type=submit> &nbsp; <input type=reset>\n");
    add("</form>");
    add("<p>" . SelectOne("select count(*) from pollvotes where pollid=?;", $pollid));
    add(" members have voted in this poll.");
    $close = SelectOne("select closedate from polls where pollid=?;", $pollid);
    if (defined($close) && $close !~ /^\s*$/) {
	add(" The poll will close on $close.");
    }
    add("\n");	
}

    
