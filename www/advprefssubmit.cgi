#!/usr/bin/perl -w
#
# Update adventure prefs
#

use strict;

use dow;

my($DonorID, $AdvHard, $AdvDone, $AdvSort, $ReturnTo);

if ($#ARGV != -1) {
    usage();
}

OpenDB();

ReadFormData();

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: advprefssubmit.cgi");
}

sub GeneratePage {
    mydo("update prefs set advdone=? where donorid=?;", $AdvDone, $DonorID);
    mydo("update prefs set advhard=? where donorid=?;", $AdvHard, $DonorID);
    if (defined($AdvSort)) {
	mydo("update prefs set advsort=? where donorid=?;", $AdvSort, $DonorID);
    }
    add("Refresh: 0;URL=$ReturnTo\n");
    add("Content-type: text/html\n\n");
    add("<html>\n<head>\n");
    add("<META HTTP-EQUIV=\"Refresh\" CONTENT=\"0;URL=$ReturnTo\">\n");
    add("<title>DOW Preferences Changed</title>\n");
    add("</head>\n");
    add("<body>\n");
    add("You should automatically be forwarded to your adventures page at <a href=\"$ReturnTo\">$ReturnTo</a>. If forwarding fails, click on the link.");
    add("</body>\n");
    add("</html>\n");
}

sub ReadFormData {
    my($buffer, @namevals, $nameval, $name, $value);
    $AdvHard = 'false';
    $AdvDone = 'false';
    $DonorID = undef;
    $AdvSort = undef;
    $ReturnTo = 'http://janin.org/dow';

    read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'}) 
	or herror("Couldn't read form data");

    # Split up into variable/value pairs

    @namevals = split(/&/, $buffer);

    # Handle quoting

    foreach $nameval (@namevals) {
	($name, $value) = split(/=/, $nameval);

	# Bit of magic from the web...
	$value =~ tr/+/ /;
	$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
	$value =~ s/<!--(.|\n)*-->//g;

	if ($name eq 'donorid') {
	    $DonorID = $value;
	} elsif ($name eq 'advhard') {
	    $AdvHard = $value;
	} elsif ($name eq 'advdone') {
	    $AdvDone = $value;
	} elsif ($name eq 'advsort') {
	    $AdvSort = $value;
	} elsif ($name eq 'returnto') {
	    $ReturnTo = $value;
	} else {
	    herror("Illegal preference '$name' in form");
	}
    }
    if (!defined($DonorID)) {
	herror("Error in form - failed to find donorid");
    }
}
