#!/usr/bin/perl -w
#
# DOW News page. This will be the new first page.
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
    herror("Usage: news.cgi");
}

sub GeneratePage {
    my($str);

    add(DOW_HTML_Header($Donor, "Database Of Wisdom (DOW)"));
    add("<h1>Database of Wisdom (DOW)</h1>\n");
#    add("DOW is brought to you by the Presidential Database and " . SelectOne("select count(*) from donors;") . " donors.\n");
    
    $str = <<'EndOfFront';
<p>Only DOW members should have access to these data. Please do not
share with anybody, especially alliances.

<p><hr><p>

DOW will be closing permanently on October 1, 2008.

<p>Given that I'm no longer playing the game, I don't want to commit to keeping DOW operational through the various rule changes indefinitely. The fixed closure date should give people plenty of time to find other options.

<p>I'm hesitant to release the code, since I don't want to risk "outing" members by having coders analyze the obfuscation methods. If somebody is really interested in the code, please let me know and we can put it to a membership vote (and give me time to generate a copy without the obfuscation routines). I developed DOW as a hobby and as an excuse to learn about SQL, so the code isn't anything I'm particularly proud of, nor will it be easy to port. If you're not familiar with perl, cgi, and postgresql, it will probably be a waste of time to get the code.

<p>I will not release the data, though if anybody wants copies of their own previous turns, I can provide them. 

<p><hr><p>

<h3>Stats</h3>

<p>Between Oct 30th, 2003 and Aug 27th, 2007, DOW was accessed 430193 times.

<p>There are a total of 212 scripts and modules.

<p>Total lines of code (including route and combat sims): 38995

<p>The database has 75 tables, with a total of 8358266 entries.


<h3>New stuff</h3>

<h3>Other Stuff</h3>
<ul>
<li>Added a page listing systems ordered by <a href="plague.cgi">plague level</a>.
<li>A list of the DOW scores of all active ships can be found at <a href="http://janin.org/dow/shipscores.cgi">http://janin.org/dow/shipscores.cgi</a>. It doesn't distinguish recent comments from old comments, but it may be useful anyway.
<li>Map view of ship locations is now available. It shows both how
frequently and how recently a ship has been at each system. Go to the
ship summary view, and select under "Full Location History" to access
it.
<li>Publicly available newbie adventures are available at <a href="http://janin.org/ninja/newbieadv.cgi">http://janin.org/ninja/newbieadv.cgi</a>. Drop me an email if you want to change your donation settings.
<li>Of interest to the Fierce, there is now a <a href="battlescore.cgi">Battle Score Calculator</a>, based on Galaxion's code. It lists all battles you've been in along with the score, so it can be slow if you fight a lot.
</ul>

All these pages can be reached from the <a href="links.cgi">Links to Other Pages</a> link.

<p><hr><p>

<h3>Please:</h3>
Please enter comments about ships you've interacted with. You can reach the comments page from the <a href="ships.cgi">Ship Summaries</a> page. Thanks!

EndOfFront

    add($str);
    add(DOW_HTML_Footer($Donor));
}

