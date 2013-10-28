#!/usr/bin/perl -w
#
# Show shop content types
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
    herror("Usage: shops.cgi");
}

sub GeneratePage {
    my($str);
    add(DOW_HTML_Header($Donor, "DOW - Shop Data"));
    $str = <<EndOfHTML;   
<h1>DOW Shop Data</h1>
<table>
<tr><th>By Module</th><th> &nbsp; </th><th>By Tech</th></tr>
<tr><td>
<table>
<tr><td><a href="shoptype.cgi?1">Warp Drives</a></td></tr>
<tr><td><a href="shoptype.cgi?2">Impulse Drives</a></td></tr>
<tr><td><a href="shoptype.cgi?3">Sensors</a></td></tr>
<tr><td><a href="shoptype.cgi?4">Cloaks</a></td></tr>
<tr><td><a href="shoptype.cgi?5">Life Support</a></td></tr>
<tr><td><a href="shoptype.cgi?6">Sickbays</a></td></tr>
<tr><td><a href="shoptype.cgi?7">Shields</a></td></tr>
<tr><td><a href="shoptype.cgi?8">Rams</a></td></tr>
<tr><td><a href="shoptype.cgi?9">Guns</a></td></tr>
<tr><td><a href="shoptype.cgi?10">Disruptors</a></td></tr>
<tr><td><a href="shoptype.cgi?11">Lasers</a></td></tr>
<tr><td><a href="shoptype.cgi?12">Missiles</a></td></tr>
<tr><td><a href="shoptype.cgi?13">Drones</a></td></tr>
<tr><td><a href="shoptype.cgi?14">Fighters</a></td></tr>
<tr><td><a href="shoptype.cgi?15">Pods</a></td></tr>
</table>
</td>
<td></td>
<td valign=top>
<table>
<tr><td><a href="shoptech.cgi?1">Primitive</a></td></tr>
<tr><td><a href="shoptech.cgi?2">Basic</a></td></tr>
<tr><td><a href="shoptech.cgi?3">Mediocre</a></td></tr>
<tr><td><a href="shoptech.cgi?4">Advanced</a></td></tr>
<tr><td><a href="shoptech.cgi?5">Exotic</a></td></tr>
<tr><td><a href="shoptech.cgi?6">Magic</a></td></tr>
</table>
</td></tr>
</table>
EndOfHTML
    add($str);
    add(DOW_HTML_Footer($Donor));
}
