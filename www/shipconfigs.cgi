#!/usr/bin/perl -w
#
# List all ships for which we have info and user can access. Link to ship configs
#

use strict;

use dow;

my $Donor = ProcessDowCommandline();

if ($#ARGV != -1) {
    usage();
}


my $AlienRE = '((Ant)|(Beetle)|(Bird)|(Cat)|(Dog)|(Elf)|(Fish)|(Goblin)|(Groundhog)|(Hamster)|(Kangaroo)|(Lizard)|(Lobster)|(Monkey)|(Otter)|(Penguin)|(Pig)|(Pixie)|(Rabbit)|(Rat)|(Sloth)|(Snake)|(Spider)|(Squirrel)|(Tiger)|(Troll)|(Turtle)|(Vole)|(Wasp)|(Weasel)|(Worm)|(Zebra)) [0-9]+';

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: shipsconfigs.cgi");
}

sub GeneratePage {
    my($sth, $row, @ships, @aliens);
    if (! $Donor->{shipconfig}) {
	herror("You must donate ship information to view ship information");
    }
    
    $sth = mydo("select distinct ship from shipconfig where donated=true order by ship;");

    while ($row = $sth->fetchrow_hashref()) {
	if ($row->{ship} =~ /$AlienRE/) {
	    push(@aliens, "<a href=\"shipconfig.cgi?$row->{ship}\">$row->{ship}</a>");
	} else {
	    push(@ships, "<a href=\"shipconfig.cgi?$row->{ship}\">$row->{ship}</a>");
	}
    }
    $sth->finish();

    add(DOW_HTML_Header($Donor, "DOW - Ship Configurations for $Donor->{ship}"));
    add("<h1>Ship Configurations for $Donor->{ship}</h1>\n");
    add("<table boder>\n");
    add(MakeHTMLTable(4, @ships, ' &nbsp; ', @aliens));
    add("</table>");
    add(DOW_HTML_Footer($Donor));
    $sth->finish();
}
