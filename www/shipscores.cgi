#!/usr/bin/perl -w
#
# For every currently active ship, show the average DOW score.
#


use strict;
use FileHandle;

use dow;

my($Donor);

$Donor = ProcessDowCommandline();

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: shipscores.cgi");
}

sub GeneratePage {
    my($turn, $sth, $row, $count);
    $turn = SelectOne("select max(turn) from turnupdate;");
    mydo("select setseed($turn/10007);");
    add(DOW_HTML_Header($Donor, "Average DOW Score for All Active Ships"));
    add("<h1>Average DOW Score for All Active Ships</h1>\n");
    add("<p>Click on the score to view the ship's comments. Click on the ship for the ship summary view.\n");
    add("<p>Note: You may notice that the score changes a bit from turn to turn. This is caused by an obfuscation method that helps keep DOW anonymous. Also, ships with a very low numbers of comments are not listed.\n");
    $count = SelectOne("select count(*) from activeships a, shipcomments c where a.turn=? and a.ship=c.ship;", $turn);
    $count = int(0.9*$count);
    $sth = mydo("select ship, count(*), avg(score), min(score), max(score) from (select c.ship, c.score from activeships a, shipcomments c where a.turn=$turn and a.ship=c.ship order by random() limit $count) as sub group by ship having count(*)>2 order by avg desc;");
    add("<table><tr><th align=left>Ship</th><th align=left># of<br>Comments&nbsp;&nbsp;&nbsp;</th><th align=left>Average&nbsp;&nbsp;<br>Score</th><th align=left>Min<br>Score&nbsp;&nbsp;</th><th align=left>Max<br>Score</tr>\n");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr><td><a href=\"shipsummary.cgi?$row->{ship}\">$row->{ship}</a></td><td>$row->{count}</td>");
	add(sprintf("<td><a href=\"viewcomments.cgi?$row->{ship}\">%3.1f</a></td><td>%3.2f</td><td>%3.2f</td></tr>\n", $row->{avg}, $row->{min}, $row->{max}));
    }
    add("</table>");
    add(DOW_HTML_Footer($Donor));
}

	
	    
    
