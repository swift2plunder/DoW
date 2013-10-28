#!/usr/bin/perl -w

use strict;
use FileHandle;

use dow;

my($FH, $PathCount, $Donor, $RSPath);

$RSPath = '/Path/to/rs';

$Donor = ProcessDowCommandline();

if ($#ARGV != 0) {
    herror("Usage: rssummary.cgi?Path\n");
}

$PathCount = $ARGV[0];
$FH = new FileHandle("$RSPath/$Donor->{donorid}.list") or herror("Couldn't find results for $Donor->{ship}");

GeneratePage();
PrintPageData();

$FH->close();
CloseDB();

exit;


sub GeneratePage {
    my($path, $line, $gotone);

    $gotone = 0;
    while ($line = <$FH>) {
	if ($line =~ /^Path ([0-9]+)$/) {
	    $path = $1;
	    if ($path == $PathCount) {
		ProcessPath($path);
		$gotone = 1;
		last;
	    }
	} 
    }
    if (!$gotone) {
	herror("Failed to find path $PathCount");
    }
}

sub ProcessPath {
    my($pathcount) = @_;
    my($line, $rest, $cur, $old, %carry, %systems, $count, $sys);
    add(DOW_HTML_Header($Donor, "Route Simulator Results $PathCount"));
    add("<h1>Route Simulator Results - Route $PathCount</h1>");
    add("<h2>WARNING!</h2><p>I'm in the process of updating the route simulator to handle the new jump costs. The results below are almost certainly wrong!</p>\n");
    add("<table border><tr><th align=left>System</th><th align=left>Sell</th><th align=left>Buy</th><th>Cash</th><th>Bonus</th></tr>\n");
    $old = undef;
    $count = 1;
    while ($line = <$FH>) {
	if ($line =~ /^\s*$/) {
	    last;
	} elsif ($line =~ /^At (.*?) with \$([0-9]+) \+ (-?[0-9]+), (.*)$/) {
	    $cur = {};
	    $cur->{sys} = $1;
	    $cur->{cash} = $2;
	    $cur->{bonus} = $3;
	    $rest = $4;
	    %carry = getcarry($rest);
	    $cur->{carry} = {%carry};
	    # do stuff here if old is set
	    if (defined($old)) {
		add("<tr>\n");
		$systems{$old->{sys}} .= "$count";
		$count++;
		add(" <td><a href=\"system.cgi?" . UncanonicalizeSystem($old->{sys}) . "\">$old->{sys}</a></td>\n");
		GetSell($cur->{carry}, $old->{carry});
		GetBuy($cur->{carry}, $old->{carry});
		add(" <td>$cur->{cash}</td>\n");
		if (defined($old)) {
		    add(" <td>$old->{bonus}</td>\n");
		} else {
		    add(" <td>0</td>\n");
		}
		add("</tr>\n\n");
	    }
	    $old = $cur;
	} else {
	    herror("Unexpected line '$line' while processing path $pathcount");
	}
    }
    add("</table>\n<p><hr><p>");
    foreach $sys (keys %systems) {
	$systems{$sys} = "<font color=\"#ff0000\">$systems{$sys}</font>&nbsp;&nbsp;";
    }
    add(MakeMapGeneral($Donor->{ship}, \%systems, "<img src=\"smallgray.gif\">"));
    add(DOW_HTML_Footer($Donor));
}	

sub GetBuy {
    my($cur, $old) = @_;
    my($nold, $n, $res);

    foreach $res (keys %{$cur}) {
	if (!exists($old->{$res})) {
	    $nold = 0;
	} else {
	    $nold = $old->{$res};
	}
	$n = $cur->{$res} - $nold;
	if ($n > 0) {
	    add(" <td>$n $res</td>\n");
	    return;		 # only able to buy one thing per system
	}
    }
    add(" <td>&nbsp;</td>\n");    # If we get here, nothing was bought
}

sub GetSell {
    my($cur, $old) = @_;
    my($ncur, $n, $res, @result);

    foreach $res (keys %{$old}) {
	if (!exists($cur->{$res})) {
	    $ncur = 0;
	} else {
	    $ncur = $cur->{$res};
	}
	$n = $old->{$res} - $ncur;
	if ($n > 0) {
	    push(@result, "$n $res");
	}
    }
    add(" <td>");
    if ($#result >= 0) {
	add(join(", ", @result));
    } else {
	add("&nbsp;");
    }
    add(" </td>\n");
}



sub getcarry {
    my($line) = @_;
    my(%ret, $n, $cap, $res, $item);
    foreach $item (split(/\s*,\s*/, $line)) {
	next if ($item =~ /^0\/[0-9]+$/);
	if ($item =~ /^([0-9]+)\/([0-9]+) (.*?)$/) {
	    $n = $1;
	    $cap = $2;
	    $res = $3;
	    $ret{$res} += $n;
	} else {
	    herror("Unexpected item $item");
	}
    }
    return %ret;
}
