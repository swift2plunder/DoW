#!/usr/bin/perl -w
#
# Regenerate .htaccess files given info from dow database.
#

use strict;
use FileHandle;
use dow;

my $DowGroupFile = '/Path/to/dow-group';
my $DowUserFile  = '/Path/to/dow';

OpenDB();

dowpw();

CloseDB();

sub dowpw {
    my($donorid, $sth, $row, $fh, $cflag);
    $cflag = '-c';
    $fh = new FileHandle(">$DowGroupFile") or die "Couldn't write dow group file $DowGroupFile: $!";
    print $fh "dow:";
    $sth = mydo("select ship, dow_pw from donors where secreturl != '' and dow_pw != '' and ship not in (select ship from frozen);");
    while ($row = $sth->fetchrow_hashref()) {
	system("/usr/sbin/htpasswd2 $cflag -b $DowUserFile \"$row->{ship}\" $row->{dow_pw}");
	$cflag = '';
	print $fh " \"$row->{ship}\"";
    }
    print $fh "\n";
    $fh->close();
}
