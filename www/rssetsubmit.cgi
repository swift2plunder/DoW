#!/usr/bin/perl -w
#
# Set route planner settings.

use strict;
use dow;

my (%Settings);
my ($Donor);

map { $Settings{$_} = undef; } qw(ood sn usn hw hwup hwne hwh hwc factory cfactory eadv euadv sadv suadv madv muadv wadv wuadv erogue srogue mrogue wrogue hiringhall prison ocean eacad sacad macad wacad eschool sschool mschool wschool contraband olympian maxjump maxpurchase nturns cargoweight system_bonuses excludepods energypercent);

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
    herror("Usage: rssetsubmit.cgi");
}

sub GeneratePage {
    add(DOW_HTML_Header($Donor, "DOW - Route Simulator Settings"));
    add("<h1>Route Simulator Settings Have Been Set</h1>");
    add("<p>The route simulator will be run at its regularly scheduled time (7am and 7pm PST). When it finishes, the results will be available on the <a href=\"rsresults.cgi\">Route Simulator Results</a> page.");
    add(DOW_HTML_Footer($Donor));
}

# Get data from form
sub ReadFormSetValues {
    my($buffer, @namevals, $nameval, $name, $value);
    read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'}) 
	or herror("Couldn't read form data");

    $Settings{excludepods} = "";

    # Split up into variable/value pairs

    @namevals = split(/&/, $buffer);

    # Handle quoting

    foreach $nameval (@namevals) {
	($name, $value) = split(/=/, $nameval);

	# Bit of magic from the web...
	$value =~ tr/+/ /;
	$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
	$value =~ s/<!--(.|\n)*-->//g;
	
	if ($name eq 'excludepods') {
	    $Settings{excludepods} .= "$value ";
	} elsif (defined($Settings{$name})) {
	    herror("Setting '$name' already set!");
	} elsif ($name eq "dow_pw") {
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

    # Everything looks good. Do the setting

    if (!ExistsSelect("select * from rss where donorid=?;", $Donor->{donorid})) {
	mydo("insert into rss values(?);", $Donor->{donorid});
    }
    foreach $name (keys %Settings) {
	mydo("update rss set $name=? where donorid=?;",
	     $Settings{$name}, $Donor->{donorid});
    }
    mydo("update rss set updated=true where donorid=?;", $Donor->{donorid});
}
