#!/usr/bin/perl -w

use strict;
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
    herror("Usage: upfdensity.cgi\n");
}

sub GeneratePage {
    my($sth, $row, %sys2count, $maxcount, $count, $sys, %label);

    $maxcount = 0;
    $sth = mydo("select system, count(*) from shiploc, banned where shiploc.ship=banned.ship and description='UPF' group by system;");

    while ($row = $sth->fetchrow_hashref()) {
	$count = int(5*sqrt($row->{count}));
	if ($count > 18) {
	    $count = 18;
	}
	$sys2count{$row->{system}} = $count;
    }
    
    add(DOW_HTML_Header($Donor, "DOW - UPF Density"));
    add("<h1>UPF Count</h1>\n");
    add("<p>Size indicates the number of times a UPF ship has been seen at a particular system. Note that this is NOT normalized to the number of times a particular system has been viewed by DOW ships. It is just a raw count.\n");

    foreach $sys (keys %sys2count) {
	if ($sys2count{$sys} > 0) {
	    $label{$sys} = sprintf("<img border=none src=\"planet.cgi?%d+%d+red\">", 
				   $sys2count{$sys}, $sys2count{$sys});
	}
    }
    add(MakeMapGeneralNew($Donor->{ship}, \%label, "<img border=none src=\"smallgray.gif\">"));
    add(DOW_HTML_Footer($Donor));
}
