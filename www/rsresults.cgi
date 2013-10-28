#!/usr/bin/perl -w

use strict;
use FileHandle;

use dow;


my($FH, $Donor, $RSPath);

$RSPath = '/Path/to/rs';

$Donor = ProcessDowCommandline();

$FH = new FileHandle("$RSPath/$Donor->{donorid}.list") or herror("Couldn't find results for $Donor->{ship}");

GeneratePage();
PrintPageData();

$FH->close();
CloseDB();

exit;


sub GeneratePage {
    my(%hops, %totalscore, %cash, %bonus, %cargo, @hops);
    my($path, $hopstr, $bonus, $oldbonus);
    my($sys, $cash, $nhops, $cargo);
    my(%first);	# First system to jump to => score

    $path = -1;
    $bonus = 0;
    $nhops = -1;

    while (<$FH>) {
	if (/^Path ([0-9]+)/) {
	    $path = $1;
	    @hops = ();
	} elsif (/^At (.*?) with \$([0-9]+) \+ (-?[0-9]+),\s*(.*)\s*$/) {
	    $sys = $1;
	    $cash = $2;
	    $oldbonus = $bonus;
	    $bonus = $3;
	    $cargo = $4;
	    push(@hops, $sys);
	} elsif (/^\s*$/) {
	    if ($path != -1) {
		pop(@hops);
		if ($nhops == -1) {
		    $nhops = $#hops+1;
		}
		if ($nhops != $#hops+1) {
		    herror("Mismatched number of hops. Should never happen! path=$path nhops=$nhops hops = " . join(", ", @hops));
		}
		$hopstr = join("", map { "<td>" . systemlink($_) . " &nbsp; </td>"; } @hops);
		if (!exists($hops{$hopstr})) {
		    $hops{$hopstr} = $path;
		    $cash{$hopstr} = $cash;
		    $bonus{$hopstr} = $oldbonus;
		    $cargo{$hopstr} = compute_cargo_value($cargo);
		    $totalscore{$hopstr} = $cash + $oldbonus + $cargo{$hopstr};
		    if (!exists($first{$hops[1]}) || $first{$hops[1]} < $totalscore{$hopstr}) {
			$first{$hops[1]} = $totalscore{$hopstr};
		    }
		}
		$path = -1;
		@hops = ();
	    }
	}
    }

    add(DOW_HTML_Header($Donor, "Route Simulator Results"));
    add("<h1>Route Simulator Results</h1>\n");
    add("<h2>WARNING!</h2><p>I'm in the process of updating the route simulator to handle the new jump costs. The results below are almost certainly wrong!</p>\n");
    add("<table>\n");    
    add("<tr><th colspan=$nhops>Route</th><th>Score</th><th>Cash</th><th>Bonus</th><th>Cargo</th></tr>\n");
    foreach $hopstr (sort { $totalscore{$b} <=> $totalscore{$a} } keys %hops) {
	add("<tr>\n");
	add(" $hopstr\n");
	add(" <td> &nbsp; $totalscore{$hopstr} &nbsp; </td>\n");
	add(" <td> &nbsp; \$$cash{$hopstr} &nbsp; </td>\n");
	add(" <td> &nbsp; $bonus{$hopstr} &nbsp; </td>\n");
	add(" <td> &nbsp; $cargo{$hopstr} &nbsp; </td>\n");
	add(" <td> &nbsp; <font size=\"-1\"><a href=\"rssummary.cgi?$hops{$hopstr}\">Details</a></font> &nbsp; </td>\n");
	add("</tr>\n");
    }  
    add("</table>\n");
    add("<p>First jumps: " . join(", ", map { systemlink($_) . " ($first{$_})"; } sort { $first{$b} <=> $first{$a} } keys(%first)) . "\n<p>\n");
    add(DOW_HTML_Footer($Donor));
}

sub compute_cargo_value {
    my($cargostr) = @_;
    my($nres, $n, $res, $tot, $row, $sth);

    $tot = 0;
    foreach $nres (split(/\s*, \s*/, $cargostr)) {
	if ($nres =~ /^([0-9]+)\/[0-9]+\s+(.*?)\s*$/) {
	    $n = $1;
	    $res = $2;
	    $tot += $n * SelectOne("select cost from factories where resource=?;",
				   $res);
	}
    }
    $sth = mydo("select cargoweight from rss where donorid=?;", $Donor->{donorid});
    $row = $sth->fetchrow_hashref();
    if (defined($row) && exists($row->{cargoweight}) && 
	defined($row->{cargoweight}) &&
	$row->{cargoweight} =~ /^\s*-?[0-9.]+\s*$/) {
	$tot *= $row->{cargoweight};
    }
    $sth->finish();
    return $tot;
}


sub systemlink {
    return "<a href=\"system.cgi?" . UncanonicalizeSystem($_[0]) . "\">$_[0]</a>";
}
