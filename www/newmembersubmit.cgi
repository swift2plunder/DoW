#!/usr/bin/perl -w
#
# Ceate a new member
#
# Called from form, so do not use ProcessDowCommandline().
# As a result, access to this page isn't logged.
#
#
# Note: dow_pw in the form is MY password, not the intended password.
# $Donor is the person who filled in the form (me), not the contents of the form.
#

use strict;

use dow;

my(%Form, $Donor, $NewDonor);

map { $Form{$_} = undef; } qw(dow_pw donorid ship label salutation email secreturl);

if ($#ARGV != -1) {
    usage();
}

OpenDB();

ReadFormData();
CreateUser();
GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: newmembersubmit.cgi");
}

sub GeneratePage {
    add(DOW_HTML_Header($Donor, "DOW - New User Created"));
    add("<h1>DOW - New User Created</h1>\n");
    add("<a href=\"ms.cgi?-u+$NewDonor->{ship}\">Membership Data</a><p>\n");
    add("<table>\n");

    add("<tr>\n");
    add(" <td>Donorid</td>\n");
    add(" <td>$NewDonor->{donorid}</td>\n");
    add("</tr>\n\n");
    
    add("<tr>\n");
    add(" <td>Ship Name</td>\n");
    add(" <td>$NewDonor->{ship}</td>\n");
    add("</tr>\n\n");

    add("<tr>\n");
    add(" <td>Label in DOW</td>\n");
    add(" <td>$NewDonor->{label}</td>\n");
    add("</tr>\n\n");

    add("<tr>\n");
    add(" <td>Salutation</td>\n");
    add(" <td>$NewDonor->{captain}</td>\n");
    add("</tr>\n\n");


    add("<tr>\n");
    add(" <td>Email</td>\n");
    add(" <td>$NewDonor->{email}</td>\n");
    add("</tr>\n\n");

    add("<tr>\n");
    add(" <td>Secret URL</td>\n");
    add(" <td>$NewDonor->{secreturl}</td>\n");
    add("</tr>\n\n");

    add("</table>\n");
    add(DOW_HTML_Footer($Donor));
}

sub CreateUser {
    mydo("insert into donors values(?, ?, ?, ?, ?, ?, null, true, true, true, true, true, true, true, true, false, false, false, false, true, false);",
	 $Form{donorid}, $Form{ship}, $Form{label}, $Form{salutation}, 
	 $Form{email}, $Form{secreturl});
    # Darn it, I can't remember which field is which...
    mydo("update donors set purgers=true where donorid=?;", $Form{donorid});

    mydo("insert into prefs values(?, false, false, 'alsne', ?, true, null, true);",
	 $Form{donorid}, "<a href=\"http://janin.org/dow/front.cgi\">Top</a>");
    $NewDonor = SelectOneRowAsHash("select * from donors where donorid=?;",
				   $Form{donorid});
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

	if (!exists($Form{$name})) {
	    herror("Unknown form element '$name'");
	} elsif (defined($Form{$name})) {
	    herror("Form element '$name' provided more than once!");
	} else {
	    $Form{$name} = $value;
	}
    }
    foreach $name (keys %Form) {
	if (!defined($Form{$name})) {
	    herror("Missing value '$name' in form");
	}
    }
    $Donor = SelectOneRowAsHash("select * from donors where dow_pw=?;",
				$Form{dow_pw});
}
