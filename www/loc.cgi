#!/usr/bin/perl -w
#
# Show location of various things of interest.
#

use strict;
use Getopt::Std;

use dow;

use vars qw($opt_m);

my($Item, $Donor);

$Donor = ProcessDowCommandline();

getopts('m') or usage();

if ($#ARGV != 0) {
    usage();
}

$Item = $ARGV[0];

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: loc.cgi?-m+Item");
}

sub GeneratePage {
    my($sth, $row, @items, $n);

    $sth = mydo("select * from statics where item=?;", $Item);
    add(DOW_HTML_Header($Donor, "DOW - $Item Locations"));
    add("<h1>DOW - $Item Locations</h1>\n");
    if ($opt_m) {
	add("Go to <a href=\"loc.cgi?$Item\">List View</a><hr>");
    } else {
	add("Go to <a href=\"loc.cgi?-m+$Item\">Map View</a><p>");
    }

    while($row = $sth->fetchrow_hashref()) {
	push(@items, $row->{system});
    }

    if ($opt_m) {
	my(@n);
	@n = ();
	add(MakeMap($Donor->{ship}, \@items, \@n));
    } else {
	$n = int($#items/10);
	if ($n <= 0) {
	    $n = 1;
	}
	add("<table border>\n");
	add(MakeHTMLTable
	    ($n, 
	     map { "<a href=\"system.cgi?" . UncanonicalizeSystem($_) . "\">$_</a>" } 
	     @items));
	add("</table>");
    }
    add(DOW_HTML_Footer($Donor));
}
