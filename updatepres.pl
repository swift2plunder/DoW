#!/usr/bin/perl -w

use strict;

use FileHandle;
use Getopt::Std;
use LWP::Simple;

use dow;

my(%ColonyToLocID);  # Map of system:resource to ref list of loc ids.
	             # E.g. Canopus:Tea => [ 126 158 ]

use vars qw($CacheFile $opt_t $opt_h);

$CacheFile = "/Path/to/turns/%d/pres.html";

$opt_t = undef;
$opt_h = undef;
getopts('ht:') or usage();
if (defined($opt_h)) {
    usage();
}
    
OpenDB();

readcolonies();	# Assigns the ColonyToLocID hash
updatepres();

CloseDB();

sub usage {
    print "Usage: updatepres.pl [-t turn]\n";
    exit;
}

sub updatepres {
    my($turn);
    if (defined($opt_t)) {
	$turn = $opt_t;
    } else {
	$turn = GetPresGateOfTruthStyle();
    }
    if (defined($turn)) {
	if (ExistsSelect("select * from turnupdate where donorid=-1 and turn=?;", $turn)) {
	    warning("Presidential report for turn $turn has already been processed.");
	} else {
	    UpdatePresGateOfTruthStyle($turn);
	}
    }
}

# Do the actual update from the cachefile.
sub UpdatePresGateOfTruthStyle {
    my($turn) = @_;
    my($fh, $line, $cachefile);
    my($header, $inTradeData, $inRogueData, $price, $price2, $system, $resource);
    message("Updating presidential database for turn $turn");
    $cachefile = sprintf($CacheFile, $turn);
    $fh = new FileHandle($cachefile) or error("Couldn't open cache of presidential report for turn $turn");
    
    $inTradeData = 0;
    $inRogueData = 0;
    while ($line = <$fh>) {
	$line =~ s/\r\n//;
	if ($line =~ /^<h3>(.*)<\/h3>$/) {
	    $header = $1;
	    if ($header eq "Trade Data by System") {
		$inTradeData = 1;
		$inRogueData = 0;
		next;
	    } elsif ($header eq "Rogue Bands") {
		$inTradeData = 0;
		$inRogueData = 1;		
	    } else {
		$inTradeData = 0;
		$inRogueData = 0;
		next;
	    }
	}
	if ($inTradeData) {
	    if ($line =~ /^\s*<td valign=\"top\">\s*(.*)\s*<\/td>\s*$/) {
		$system = $1;
		message(" Presidential Database at $system");
	    } elsif ($line =~ /^\s*(.*?)\s*-\s*([0-9]+)(,\s*([0-9]+))?\s*<br>\s*$/) {
		if (!defined($system)) {
		    error(" System not defined while parsing Presidential Database");
		    return;
		}
		$resource = $1;
		$price = $2;
		$price2 = $4;
		if (ExistsTradePrice($system, $resource, $price, $turn, -1)) {
		    message("$resource for \$$price (confirmed)");
		} else {
		    mydo("insert into trade values(default, ?, ?, ?, ?, ?, ?);",
			 $system, $resource, $price, $turn, -1, 
			 $ColonyToLocID{$system . ":" . $resource}[0]);
		    message("$resource for \$$price (entered)");
		}
		if (defined($price2)) {
		    if (ExistsTradePrice($system, $resource, $price2, $turn, -1)) {
			message("$resource for \$$price2 (confirmed)");
		    } else {
			mydo("insert into trade values(default, ?, ?, ?, ?, ?, ?);",
			     $system, $resource, $price2, $turn, -1,
			     $ColonyToLocID{$system . ":" . $resource}[1]);
			message("$resource for \$$price2 (entered)");
		    }
		}
	    }
	} elsif ($inRogueData) {
	    if ($line =~ m|<td valign="top">(.*)</td>|) {
		$system = $1;
	    } elsif ($line =~ m|([a-z]+) ([a-z]+) in Gas Giant \(([0-9]+)%\)<br>|i) {
		AddRogueBand($system, $1, $2, 'Impulse', $3, $turn);
	    } elsif ($line =~ m|([a-z]+) ([a-z]+) in Badland \(([0-9]+)%\)<br>|i) {
		AddRogueBand($system, $1, $2, 'Life Support', $3, $turn);
	    }
	}
    }
    $fh->close();
    mydo("insert into turnupdate values($turn, -1);");
} # UpdatePresGateofTruthStyle()

# Download the pres database. Store in cache. Return the turn it's for
# or undef if already processed for that turn.

sub GetPresGateOfTruthStyle {
    my($url, $fh, $content, $turn, $cachefile);

#   Gate of Truth:
#    $url = 'http://www.wolfandweasel.com/tbg/pfoio.htm';

#   Scoop's Voyage
#    $url = 'http://sv.hainish.de/president.html';

#   Lost Hope
    $url = 'http://www.thirteen.dynu.com/tbg/data.html';

    $content = myget($url);
    if (!defined($content)) {
	error("Couldn't retrieve Presidential Database at $url");
    }
    if ($content =~ /<h2>Report for turn (.*)<\/h2>/) {
	$turn = $1;
    } else {
	error("Couldn't find turn in presidential report at $url");
    }
    if (ExistsSelect("select * from turnupdate where donorid=-1 and turn=?;", $turn)) {
	warning("Presidential report for turn $turn has already been processed.");
	return undef;
    }
    $cachefile = sprintf($CacheFile, $turn);
    if (-e $cachefile) {
	warning("Presidential report for turn $turn already exists.");
    } else {
	message("Storing presidential report for turn $turn");
	$fh = new FileHandle(">$cachefile") or error("Couldn't write to $cachefile: $!");
	print $fh $content;
	$fh->close();
    }
    return $turn;
} # GetPresGateOfTruthStyle()

sub message {
    my $str = join(' ', @_);
    print "$str\n";
}

sub warning {
    my $str = join(' ', @_);
    print STDERR "Warning: $str\n";
}

sub error {
    my $str = join(' ', @_);
    print STDERR "ERROR: $str\n";
    exit;
}

# Get the given URL.
# Tries three times.
# On success, return the contents.
# On failure, returns undef.

sub myget {
    my($url) = @_;
    my($content, $try);
    for ($try = 0; $try < 3; $try++) {
	$content = get($url);
	if (!defined($content)) {
	    warning("myget($url) failed, try $try");
	} else {
	    return $content;
	}
    }
    warning("myget($url) failed too many times. Giving up.");
    return undef;
}

#
# Check if the given system/resource/turn has already been
# entered. If so, confirm the prices are the same, and return 1.
# If not, return 0.
#

sub ExistsTradePrice {
    my($system, $resource, $price, $turn, $donorid) = @_;
    my($sth, $oldprice, $row, $gotone);
    $sth = mydo("select price, donorid from trade where system=? and resource=? and turn=?;", $system, $resource, $turn);
    $gotone = 0;
    while ($row = $sth->fetchrow_hashref()) {
	next if $row->{donorid} == $donorid;
	$gotone = 1;
	if ($row->{price} == $price) {
	    $sth->finish();
	    return 1;
	}
    }
    if ($gotone) {
	error("Price conflict! $system $resource $turn $price");
    }
    $sth->finish();
    return 0;
}

sub AddRogueBand {
    my($system, $race, $field, $location, $danger, $turn) = @_;
    if (ExistsSelect("select race from rogues where race=? and field=? and location=? and danger=? and system=? and turn=?;",
		     $race, $field, $location, $danger, $system, $turn)) {
	message("$race Rogue band (confirmed)");
    } else {
	mydo("insert into rogues values(?, ?, ?, ?, ?, ?);",
	     $race, $field, $location, $danger, $system, $turn);
	message("$race Rogue band (inserted)");
    }
}

sub readcolonies {
    my($sth, $row);
    $sth = mydo("select * from colonies;");
    while ($row = $sth->fetchrow_hashref()) {
	push(@{$ColonyToLocID{$row->{system} . ":" . $row->{resource}}}, $row->{id});
    }
    $sth->finish();
}
