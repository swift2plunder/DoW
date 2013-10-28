#!/usr/bin/perl -w
#
# Institute of Xenology, add history entry
#

use strict;
use dow;

my(%Form, $Donor);

map { $Form{$_} = undef; } qw (dow_pw ship turn action);

if ($#ARGV != -1) {
    usage();
}

OpenDB();

ReadFormData();

# Allow only an admin OR the ship being added to add data.
#
#if (!$Donor->{admin} && $Donor->{ship} ne $Form{ship}) {
#    herror("You may only enter Xenology actions for your own ship");
#}
#
# Changed to just allow xenoadmin

if (!$Donor->{xenoadmin}) {
    herror("Only the Admin may use this page");
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: xeno_add_entry.cgi");
}

sub GeneratePage {
    add("Refresh: 0;URL=http://janin.org/dow/xeno.cgi\n");
    add("Content-type: text/html\n\n");
    add("<html>\n<head>\n");
    add("<META HTTP-EQUIV=\"Refresh\" CONTENT=\"0;URL=http://janin.org/dow/xeno.cgi\">\n");
    add("<title>Xenologist Entry Added</title>\n");
    add("</head>\n");
    add("<body>\n");
    add("Xenology entry for $Form{ship} on turn $Form{turn} added.<p>Action: $Form{action}.<p>\n");
    add("You should be returned to the <a href=\"xeno.cgi\">Xenology</a> page shortly.\n");
    add("</body>\n");
    add("</html>\n");
    mydo("insert into xeno_history values(default, ?, ?, ?);", $Form{ship}, $Form{turn}, $Form{action});
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
    $Donor = SelectOneRowAsHash("select * from donors where dow_pw=?;", $Form{dow_pw});
}
