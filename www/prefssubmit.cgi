#!/usr/bin/perl -w
#
# Update prefs
#
# Called from form, so do not use ProcessDowCommandline().
# As a result, access to this page isn't logged.
#

use strict;

use dow;

my($DonorID, %Prefs);

%Prefs = (
	  'advhard' => 'false',
	  'advdone' => 'false',
	  'onlyprefadv' => 'false',
	  'mapinsys' => 'false',
	  'showleftbar' => 'false',
	  'advsort' => 'alsn',
	  'bottombar' => undef,
	  'leftbarwidth' => 150,
	  'prefadvmin' => 0,
	  'prefadvmax' => 32
	  );

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
    herror("Usage: prefssubmit.cgi");
}

sub GeneratePage {
    my($ship, $key);

    $ship = SelectOne("select ship from donors where donorid=?;", $DonorID);

    foreach $key (keys %Prefs) {
	mydo("update prefs set $key=? where donorid=?;", $Prefs{$key}, $DonorID);
    }

    # Intentially use undef for donor so that any misset prefs don't screw up page.
    add(DOW_HTML_Header(undef, "DOW View Preferences for $ship Set"));
    add("<p>DOW view preferences for $ship have been set.\n");
    add("<p>Return to <a href=\"prefs.cgi\">Preferences</a>.<br>\n");
    add("Go to <a href=\"front.cgi\">DOW top</a>.");
    add(DOW_HTML_Footer(undef));
}

sub ReadFormData {
    my($buffer, @namevals, $nameval, $name, $value);
    $DonorID = undef;

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
	} elsif (exists($Prefs{$name})) {
	    $Prefs{$name} = $value;
	} else {
	    herror("Illegal preference '$name' in form");
	}
    }
    if (!defined($DonorID)) {
	herror("Error in form - failed to find donorid");
    }
}
