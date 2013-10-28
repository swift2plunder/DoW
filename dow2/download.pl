#!/usr/bin/perl -w
#
# Recursively download data (from the TBG server) based
# on entries in the downloadfiles table.
#

use strict;
use Getopt::Std;
use LWP::Simple;

use dow2;

# Command line options

use vars qw($opt_t);

# Global variables

my @OrigARGV = @ARGV;

my $Turn;

my $ArchivePath;	# Where to store stuff

OpenDB("dow2");

# Use the value in params.turn unless -t is specified.

$opt_t = SelectOneWithDefault("select processturn from params;", undef);

getopts('t:') or usage();

if (!defined($opt_t)) {
    error("Unable to automatically determine turn. Please use download.pl -t turn.");
}

$Turn = $opt_t;

OpenLogs("download", $Turn);
message("\n----------\ndownload.pl called with arguments '" . join(" ", @OrigARGV) . "' on " .  `date`);

$ArchivePath = SelectOne("select topdir from params;") . "/" . SelectOne("select archive from params;") . "/$Turn";

# Create the directory if needed
if (! -d $ArchivePath) {
    message("Creating directory $ArchivePath");
    mkdir($ArchivePath) or error("Couldn't create archive dir '$ArchivePath': $!");
}

process_all();

message("download.pl finished on " . `date`);
CloseLogs();
CloseDB();

exit;

# All subs below here.

######################################################################
#
# Download all files in the downloadfiles table, starting with
# ones that haven't been tried yet. Repeat until there are no
# files to download.
#

sub process_all {
    my($sth, $row, $gotone);

    $sth = mydo("select * from downloadfiles where turn=$Turn and (status='Start' or status='Downloaded') order by failures;");
    while ($row = $sth->fetchrow_hashref()) {
	if ($row->{status} eq 'Start') {
	    if (download($row)) {
		$gotone = 1;
	    }
	} elsif ($row->{status} eq 'Downloaded') {
	    if (recurse($row)) {
		$gotone = 1;
	    }
	}
    }
    $sth->finish();
    if ($gotone) {
	process_all();
    }
}  # process_all()

sub download {
    my($data) = @_;
    my($contents);
    if (-e "$ArchivePath/$data->{filename}") {
	warning("The file $data->{filename} already exists. Skipping.");
	mydo("update downloadfiles set status='Downloaded' where id=?;",
	     $data->{id});
	return 1;
    }
    $contents = myget($data->{url});
    if (defined($contents)) {
	if (validate_turn($data, $contents)) {
	    mystore($contents, "$ArchivePath/$data->{filename}");
	    mydo("update downloadfiles set status='Downloaded' where id=?;",
		 $data->{id});
	    message("$data->{filename} downloaded.");
	    return 1;
	}
    }
    mydo("update downloadfiles set failures=? where id=?;",
	 SelectOne("select failures from downloadfiles where id=?;", $data->{id}) + 1,
	 $data->{id});
    # Warning were already issued in myget and validate_turn, so just return failure.
    return 0;
}

# Go through the file, looking for more to process. As with the script
# that updates the pages, this is somewhat adhoc.

sub recurse {
    my($data) = @_;
    if ($data->{type} eq 'Player') {
	return recurse_player($data);
    } else {
	mydo("update downloadfiles set status='Traversed' where id=?;", $data->{id});
	return 0;
    }
}

sub recurse_player {
    my($data) = @_;
    my($fh, $line, $url, $ship, $filename);
    $fh = new FileHandle("$ArchivePath/$data->{filename}") or error("Couldn't open file $data->{filename}: $!");
    while ($line = <$fh>) {
	while ($line =~ m|<A HREF=\"(http://tbg.fyndo.com/tbg/Ship_.*?\.htm)\">(.*?)</A>|g) {
	    $url = $1;
	    $ship = $2;
	    $filename = NameToFilename($ship) . ".ship.html";
	    InsertUnique("downloadfiles", 
			 { turn => $Turn,
			   filename => $filename,
			   url => $url,
			   status => 'Start',
			   type => 'Ship',
			   name => $ship },
			 qw( name turn type ));
	}
    }
    $fh->close();
    mydo("update downloadfiles set status='Traversed' where id=?;", $data->{id});
    return 1;
}				     
    
sub usage {
    print STDERR "\nUsage: $0 [-t turn]\n";
    print STDERR "\n\tDownload data (typically from the TBG server) based on entries in the downloadfiles table. If -t turn is specified, use that turn. Otherwise, use the turn stored in params.processturn. The turn must match the turn entries in downloadfiles.\n\n";
    exit;
}

# Get the URL and return it as a string.
# Try 3 times. If all three fail, return undef.

sub myget {
    my($url) = @_;
    my($try, $ret);
    for ($try = 0; $try < 3; $try++) {
    	$ret = get($url);
	if (!defined($ret)) {
	    warning("myget($url) failed, try $try");
	} else {
	    return $ret;
	}
    }
    warning("myget($url) failed too many times. Giving up.");
    return undef;
}

sub mystore {
    my($content, $filename) = @_;
    my($fh);
    $fh = new FileHandle(">$filename") or error("Couldn't write file '$filename': $!");
    print $fh $content;
    $fh->close();
}

sub validate_turn {
    my($data, $content) = @_;
    my($ship, $turn);
    if ($data->{type} eq 'Player') {
	if ($content =~ m|^<H1>To Boldly Go - Starship (.*?), Turn ([0-9]+)</H1>$|m) {
	    $ship = $1;
	    $turn = $2;
	    if (($ship ne $data->{name}) || ($turn != $Turn)) {
		warning("Mismatched ship/turn in player page. Got $ship, $turn. Expected $data->{name}, $Turn.");
		return 0;
	    }
	} else {
	    warning("Couldn't extract heading from player page $data->{name}.");
	    return 0;
	}
    } elsif ($data->{type} eq 'SST') {
	if ($content =~ m|^<H1>Issue ([0-9]+) - Stardate [0-9.]+</H1>$|m) {
	    $turn = $1;
	    if ($turn != $Turn) {
		warning("Mismatch turn in SST. Got $turn, expected $Turn.");
		return 0;
	    }
	} else {
	    warning("Couldn't extract heading from SST.");
	}
    } elsif ($data->{type} eq 'Alias File') {
	# Turn isn't embedded. No error checking.
    } elsif ($data->{type} eq 'Ship') {
	if ($content =~ m|^<HTML><HEAD><TITLE>(.*), Turn ([0-9]+)</TITLE></HEAD>$|m) {
	    $ship = $1;
	    $turn = $2;
	    if (($ship ne $data->{name}) || ($turn != $Turn)) {
		warning("Mismatched ship/turn in ship page. Got $ship, $turn. Expected $data->{name}, $Turn.");
		return 0;
	    }
	} else {
	    warning("Couldn't extract heading from ship page $data->{name}.");
	    return 0;
	}
    } else {
	error("Unexpected type $data->{type} in validate_turn!");
    }
    return 1;
}
