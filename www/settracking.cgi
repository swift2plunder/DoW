#!/usr/bin/perl -w
#
# Set who you track. For use with tracking.cgi.
#

use strict;

use dow;

my($Donor);

if (exists($ENV{REMOTE_USER})) {
    $Donor = ProcessDowCommandline();
} elsif (exists($ENV{CONTENT_LENGTH})) {
    ProcessFormData();
} else {
    herror("Couldn't get remote_user or form data!");
}

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: settracking.cgi");
}

sub GeneratePage {
    my($sth, $row, $turn);
    $turn = SelectOne("select max(turn) from turnupdate;");
    add(DOW_HTML_Header($Donor, "Add/Remove tracked ship"));
    add("<h1>Add/Remove Tracked Ships</h1>\n");
    add("This page allows you to add and remove ships to be tracked. To view the tracked ships, go to the <a href=\"tracking.cgi\">Tracking</a> page.<p>\n");
    add("<hr>\n");
    
    add("<form method=post action=\"settracking.cgi\">\n");
    add("<input type=hidden name=dow_pw value=\"$Donor->{dow_pw}\">\n");
    add("The following ships are currently being tracked. Select ships to no longer track them.<br>\n");
    add("<select name=remove size=6 multiple>\n");
    $sth = mydo("select tracked from tracking where ship=?;", $Donor->{ship});
    while ($row = $sth->fetchrow_hashref()) {
	add("<option>$row->{tracked}</option>\n");
    }
    $sth->finish();
    add("</select><br>");
    add("<p>To track additional ships, select them below.<br>\n");
    add("<select name=add size=6 multiple>\n");
    $sth = mydo("select ship from activeships where turn=? and ship not in (select tracked from tracking where ship=?) order by ship;", $turn, $Donor->{ship});
    while ($row = $sth->fetchrow_hashref()) {
	add("<option>$row->{ship}</option>\n");
    }
    $sth->finish();
    add("</select><br>");
    add("<p><input type=submit> &nbsp; <input type=reset></form>");
    add(DOW_HTML_Footer($Donor));
}


sub ProcessFormData {
    my($buffer, @namevals, $nameval, $name, $value);
    my(@toadd, @toremove);

    OpenDB();

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

	if ($name eq 'dow_pw') {
	    $Donor = SelectOneRowAsHash("select * from donors where dow_pw=?;",
					$value);
	} elsif ($name eq 'add') {
	    push(@toadd, $value);
	} elsif ($name eq 'remove') {
	    push(@toremove, $value);
	} else {
	    herror("Illegal tag $name in form");
	}
    }
    foreach $name (@toremove) {
	mydo("delete from tracking where ship=? and tracked=?;",
	     $Donor->{ship}, $name);
    }
    foreach $name (@toadd) {
	mydo("insert into tracking values(?, ?);", $Donor->{ship}, $name);
    }
}
