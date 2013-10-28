#!/usr/bin/perl -w
#
# Enter a comment about a ship.
#
# Called from form, so do not use ProcessDowCommandline().
# As a result, access to this page isn't logged.
#

use strict;
use dow;

my(%Form);

map { $Form{$_} = undef; } qw (donorid ship turn score comment);

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
    herror("Usage: commentsubmit.cgi");
}

sub GeneratePage {
    my($donor, $sth);
    $sth = mydo("select * from donors where donorid=?;", $Form{donorid});
    $donor = $sth->fetchrow_hashref();
    if (!defined($donor)) {
	herror("Couldn't get donor. This shouldn't happen!");
    }
    if ($donor->{label} =~ /^Anonymous/) {
	herror("No anonymous comments are allowed. Sorry.");
    }
    if ($Form{turn} !~ /^[0-9]+$/) {
	$Form{turn} = 0;
    }
    mydo("insert into shipcomments values(default, ?, ?, ?, ?, ?, default);",
	 $Form{donorid}, $Form{ship}, $Form{turn}, $Form{score}, $Form{comment});

    add(DOW_HTML_Header($donor, "Comment about $Form{ship} submitted"));
    add("<p>Comment about $Form{ship} on turn $Form{turn} has been set.\n");
    add("<p>Score: $Form{score}");
    add("<p>Comment: <table><tr><td>$Form{comment}</td></tr></table>");
    add("\n<p>Return to summary of <a href=\"shipsummary.cgi?$Form{ship}\">$Form{ship}</a>.<br>");
    add("Go to <a href=\"front.cgi\">DOW top</a>.");
    add(DOW_HTML_Footer($donor));
}

sub ReadFormData {
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

	if (exists($Form{$name}) && !defined($Form{$name})) {
	    $Form{$name} = $value;
	} else {
	    herror("Illegal or duplicate form element '$name' in form");
	}
    }
    foreach $name (keys %Form) {
	if (!defined($Form{$name})) {
	    herror("Missing form element '$name' in form");
	}
    }
}
