#!/usr/bin/perl -w
#
# DOW Links
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
    herror("Usage: links.cgi");
}

sub GeneratePage {
    my($str);

    add(DOW_HTML_Header($Donor, "DOW Links"));
    $str = <<'EndOfLinks';
<ul>
<li><a href="dowinfo.html">Miscellaneous DOW Policies and Information</a>.
<li><a href="plague.cgi">Plague</a> levels of each system.
<li>A list of the DOW scores of all active ships can be found at <a href="http://janin.org/dow/shipscores.cgi">http://janin.org/dow/shipscores.cgi</a>. It doesn't distinguish recent comments from old comments, but it may be useful anyway.
<li>Publicly available newbie adventures are available at <a href="http://janin.org/ninja/newbieadv.cgi">http://janin.org/ninja/newbieadv.cgi</a>. Drop me an email if you want to change your donation settings.
<li>Of interest to the Fierce, there is now a <a href="battlescore.cgi">Battle Score Calculator</a>, based on Galaxion's code. It lists all battles you've been in, along with the score. It can be slow if you fight a lot.
<li>Information on <a href="http://janin.org/ninja/purges.cgi">Terminal purges</a>.
<li>Information on <em>A Mad Ninja's</em> <a href="http://janin.org/ninja/tradesim.html">trade route simulator</a>.
<li>Random <a href="http://janin.org/ninja/newbie.html">tips</a> for newbies. See also the <a href="http://janin.org/dow/wiki/index.cgi">DOW Wiki</a> for an expanded version.
<li>Ships <a href="http://janin.org/ninja/banned.cgi">banned</a> from DOW.
<li>DOW Administrator <a href="todo.html">To Do</a> list.

</ul>

<h3>Beta and Experimental Pages</h3>

<ul>
<li>List of ships by <a href="powerrank.cgi">power rank</a>.
<li>The <a href="configulator.cgi">configulator</a>, a tool that answers questions like "what would my warp percentage be if I sold my Basic modules".
<li><a href="upfdensity.cgi">UPF Density Map View</a>
<li>Trade price history by: <a href="thsys.cgi">System</a> &nbsp; <a href="thres.cgi">Resource</a> &nbsp; <a href="tradehistory.cgi">System/Resource</a>
<li><a href="plotdowaccess.cgi">Graph of DOW Accesses by turn</a>
<li>Ship Density &nbsp; <a href="density.cgi">List</a> &nbsp <a href="density.cgi?-m">Map</a>
</ul>
EndOfLinks

    add($str);
    add(DOW_HTML_Footer($Donor));
}

