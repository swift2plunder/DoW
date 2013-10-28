#!/usr/bin/perl -w

use strict;
use File::Find;
use FileHandle;
use Archive::Zip qw( :ERROR_CODES :CONSTANTS );
use IO::Scalar;

use dow;

my($TurnDir, $Donor, $Zip, $StartTurnArg, $EndTurnArg, $StartTurn, $EndTurn, $GotOne);

$TurnDir = '/Path/to/turns';

$Donor = ProcessDowCommandline();

if ($#ARGV != 1) {
    usage();
}

$StartTurnArg = shift;
$EndTurnArg = shift;

$StartTurn = 99999;
$EndTurn = -9999;
$GotOne = 0;

GeneratePage();
CloseDB();
exit;

sub usage {
    herror("Usage: turnzip.cgi?StartTurn+EndTurn");
}

sub GeneratePage {
    my($sh, $data);
    $Zip = Archive::Zip->new();
    find(\&wanted, $TurnDir);
    $sh = new IO::Scalar \$data;
    unless ( $Zip->writeToFileHandle($sh) != AZ_OK ) {
  #      herror("Failed to write zip file.");
    }
    if (!$GotOne) {
	herror("No turns found!");
    }
    print "Content-type: application/zip\n";
    print "Content-length: ", length($data), "\n";
    print "Content-Disposition: attachment; filename=\"", $Donor->{ship}, "$StartTurn-$EndTurn.zip\"";
    print "\n\n";
    print $data;
}

sub wanted {
    my($turn);
    if ($File::Find::name =~ m|$TurnDir/([0-9]+)/$Donor->{donorid}\.html$|) {
	$turn = $1;
	if ($StartTurnArg <= $turn && $turn <= $EndTurnArg) {
	    $GotOne = 1;
	    $Zip->addFile($File::Find::name, "$turn.html");
	    if ($turn < $StartTurn) {
		$StartTurn = $turn;
	    }
	    if ($turn > $EndTurn) {
		$EndTurn = $turn;
	    }
	}
    }
}
