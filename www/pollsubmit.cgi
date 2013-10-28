#!/usr/bin/perl -w
#
# Set poll results

use strict;
use dow;

my (%Settings);
my ($Donor);

map { $Settings{$_} = undef; } qw(dow_pw pollid item);

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
    herror("Usage: pollsubmit.cgi");
}

sub GeneratePage {
    my($ReturnTo);
    $ReturnTo = "http://janin.org/dow/poll.cgi";
    add("Refresh: 0;URL=$ReturnTo\n");
    add("Content-type: text/html\n\n");
    add("<html>\n<head>\n");
    add("<META HTTP-EQUIV=\"Refresh\" CONTENT=\"0;URL=$ReturnTo\">\n");
    add("<title>DOW Preferences Changed</title>\n");
    add("</head>\n");
    add("<body>\n");
    add("You should automatically be forwarded to the polls page at <a href=\"$ReturnTo\">$ReturnTo</a>. If forwarding fails, click on the link.");
    add("</body>\n");
    add("</html>\n");
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
	} 
	if (!exists($Settings{$name})) {
	    herror("Unexpected setting '$name'!");
	}
	if ($name eq "dow_pw") {
	    $Donor = SelectOneRowAsHash("select * from donors where dow_pw=?;", $value);
	}
	$Settings{$name} = $value;
    }
    # Make sure all are set
    foreach $name (keys %Settings) {
	if (!defined($Settings{$name})) {
	    herror("Missing value for setting '$name'!");
	}
    }
    
    # Everything looks good. Do the setting
    mydo("delete from pollvotes where donorid=? and pollid=?", $Donor->{donorid},
	 $Settings{pollid});
    mydo("insert into pollvotes values(?, ?, ?);", $Donor->{donorid}, $Settings{item},
	 $Settings{pollid});
}
