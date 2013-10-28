#!/usr/bin/perl -w

use strict;
use dow;

my (%Settings);
my ($Donor);

map { $Settings{$_} = undef; } qw(email secreturl dow_pw adv_newbie adv_done adv_high adv_hard adv_all shiploc shipconfig influence pub_adv_newbie pub_shop_newbie pub_trade obfuscate anonymous purgers);

if ($#ARGV != -1) {
    usage();
}

OpenDB();

ReadFormSetValues();
GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: mssubmit.cgi");
}

sub GeneratePage {
    add(DOW_HTML_Header($Donor, "Member Settings"));
    add("<h1>New Settings Have Been Recorded</h1>");
    add("<p>The changes will take effect after the next turn update.\n");
    add(DOW_HTML_Footer($Donor));
}

# Get data from form
sub ReadFormSetValues {
    my($buffer, @namevals, $nameval, $name, $value);
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
	
	if (defined($Settings{$name})) {
	    herror("Setting '$name' already set!");
	} elsif ($name eq "current_dow_pw") {
	    $Donor = SelectOneRowAsHash("select * from donors where dow_pw=?;", 
					$value);
	} elsif (!exists($Settings{$name})) {
	    herror("Unexpected setting '$name'!");
	} else {
	    $Settings{$name} = $value;
	}
    }
    # Make sure all are set
    foreach $name (keys %Settings) {
	if (!defined($Settings{$name})) {
	    herror("Missing value for setting '$name'!");
	}
    }

    # Validation of some settings.

    if (!defined($Donor) && !exists($Donor->{donorid})) {
	herror("Illegal donor information. This should never happen!");
    }

    if ($Settings{secreturl} !~ m|^http://tbg.fyndo.com/tbg/[A-Z][a-z]*\.htm$| &&
	$Settings{secreturl} !~ m|^http://tbg.fyndo.com/tbg/share_[A-Z][a-z]*\.htm$|) {
	herror("Your secret URL \"$Settings{secreturl}\" doesn't look like a valid TBG secreturl (e.g. \"http://tbg.fyndo.com/tbg/Chalatrefy.htm\").");
    }

    if ($Settings{dow_pw} =~ /[\"\']/) {
	herror("Please don't use quotes in your DOW password");
    }

    if ($Settings{email} !~ /^[a-zA-Z0-9_.-]+\@[a-zA-Z0-9_.-]+$/) {
	herror("Your email address \"$Settings{email}\" doesn't look valid. Please contact the DOW admin if it really is valid.\n");
    }

    if ($Settings{adv_all} eq "Yes") {
	foreach $name (qw(adv_newbie adv_done adv_high adv_hard)) {
	    $Settings{$name} = "Yes";
	}
    }

    # Everything looks good. Do the setting

    mydo("delete from newsettings where donorid=?;", $Donor->{donorid});
    mydo("insert into newsettings values (?, ?);", $Donor->{donorid}, $Donor->{ship});
    foreach $name (keys %Settings) {
	mydo("update newsettings set $name=? where donorid=?;",
	     $Settings{$name}, $Donor->{donorid});
    }
}
