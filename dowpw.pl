#!/usr/bin/perl -w
#
# Change or create the password of a user of dow.
#
# For security reasons, I've removed the actual code for GenPW().
#

use strict;
use FileHandle;
use Getopt::Std;
use dow;

use vars qw($opt_v $opt_p $opt_h);

srand(time ^ $$);

my $Verbose = 1;
my $Password;
my $DowGroupFile = '/Path/to/.htaccess_info/dow-group';
my $DowUserFile  = '/Path/to/.htaccess_info/dow';
my %InGroupFile;

$opt_h = 0;

getopts("hp:v") || usage();
usage() if $opt_h;

my $Ship = join(" ", @ARGV);

if ($opt_v) {
    $Verbose = !$Verbose;
}

if ($opt_p) {
    $Password = $opt_p;
} else {
    $Password = GenPW();
}

ReadGroupFile();

OpenDB();

dowpw();

CloseDB();

WriteGroupFile();

sub usage {
    print STDERR "Usage: dowpw [-v] [-h] [-p \"password\"] ship name\n";
    exit;
}

sub dowpw {
    my($donorid, $sth, $row);
    $sth = mydo("select donorid, dow_pw from donors where ship=?;", $Ship);
    $row = $sth->fetchrow_hashref();
    if (!defined($row)) {
	print STDERR "Couldn't find ship $Ship in donors list!\n";
	exit;
    }
    $donorid = $row->{donorid};
    $InGroupFile{$Ship} = 1;
    if (!exists($row->{dow_pw}) || !defined($row->{dow_pw})) {
	pv("Password for $Ship does not exist. Creating password $Password.");
    } else {
	pv("Changing password for $Ship from $row->{dow_pw} to $Password.");
    }
    mydo("update donors set dow_pw=? where donorid=?;", $Password, $donorid);
    system("/usr/sbin/htpasswd2 -b $DowUserFile \"$Ship\" $Password");
}

sub ReadGroupFile {
    my($fh, $line);

    $fh = new FileHandle($DowGroupFile) or die "Couldn't open DOW Group file $DowGroupFile: $!";
    $line = <$fh>;
    $fh->close();
    while ($line =~ /\"(.*?)\"/g) {
	$InGroupFile{$1} = 1;
    }
}

sub WriteGroupFile {
    my($fh, $key);

    $fh = new FileHandle(">$DowGroupFile") or die "Couldn't write DOW Group file $DowGroupFile: $!";

    print $fh "dow:";
    foreach $key (keys %InGroupFile) {
	print $fh " \"$key\"";
    }
    print $fh "\n";
    
    $fh->close();
}


sub GenPW {
    die "For security reasons, the code for generating passwords has been removed. You should reimplement.";
}


sub pv {
    if ($Verbose) {
	print join(" ", @_), "\n";
    }
}
