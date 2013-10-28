#!/usr/bin/perl -w

use strict;
use Getopt::Std;
use dow;

use vars qw($opt_m);

my($Donor);

$Donor = ProcessDowCommandline();

getopts('m') or usage();

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: density.cgi\n");
}

sub GeneratePage {
    my($sth, $row, %tot, %n, %av, $sys, %score, $score, %label);
    my($minscore, $maxscore);

    map { $n{$_} = 0; $av{$_} = 0; } SelectAll("select system from starcoords;");

    $sth = mydo("select * from systemviewed;");
    while ($row = $sth->fetchrow_hashref()) {
	$tot{$row->{system}} += 
	    SelectOne("select count(*) from shiploc where system=? and turn=?;",
		      $row->{system}, $row->{turn});
	$n{$row->{system}}++;
    }
    foreach $sys (keys %tot) {
	$av{$sys} = sprintf("%.1f", $tot{$sys} / $n{$sys});
    }
    
    add(DOW_HTML_Header($Donor, "DOW - Visitation Density"));
    add("<h1>DOW - Visitation Density</h1>\n");
    if (defined($opt_m)) {
	add("<p>Size indicates density in ships per turn. A <font color=\"#00ff00\">?</font> means that there is no data on visitations to the system.");
	add("<p>Go to <a href=\"density.cgi\">List View</a><hr><p>\n");
	# Remap values here (e.g. log, truncate high)
	foreach $sys (keys %av) {
	    if ($av{$sys} > 8) {
		$score{$sys} = 8;
	    } else {
		$score{$sys} = $av{$sys};
	    }
	}
	# Rescale and assign label
	$minscore = 100000;
	$maxscore = -10000;
	foreach $sys (keys %score) {
	    if ($score{$sys} < $minscore) {
		$minscore = $score{$sys};
	    }
	    if ($score{$sys} > $maxscore) {
		$maxscore = $score{$sys};
	    }
	}
	foreach $sys (keys %score) {
	    $score = 4+int(12*($score{$sys} - $minscore) / ($maxscore - $minscore+1));
	    if ($n{$sys} > 0) {
		$label{$sys} = sprintf("<img src=\"planet.cgi?%d+%d+green\">", $score, $score);
	    } else {
		$label{$sys} = "<font color=\"#00ff00\">?</font>&nbsp;";
	    }
	}
	add(MakeMapGeneral($Donor->{ship}, \%label, "&nbsp;"));
    } else {
	add("<p>This table lists the average density (ships/turn). The \"#Views\" column indicates how many times the system has been seen by DOW (e.g. DOW members in system, terminal reports, probe reports). If the number is low, the density figure will be unreliable.\n");
	add("<p>Go to <a href=\"density.cgi?-m\">Map View</a>\n");
	add("<p><hr><p>\n");
	
	add("<table>\n");
	add("<tr>\n");
	add(" <th align=left>System</th>\n");
	add(" <th align=left>#Views</th>\n");
	add(" <th align=left>Density</th>\n");
	add("</tr>\n");
	foreach $sys (sort { $av{$a} <=> $av{$b} } keys %av) {
	    add("<tr>\n");
	    add(" <td><a href=\"system.cgi?" . UncanonicalizeSystem($sys) . "\">$sys</a>&nbsp;&nbsp;</td>\n");
	    add(" <td>$n{$sys}</td>\n");
	    if ($n{$sys} > 0) {
		add(" <td>$av{$sys}</td>\n");
	    } else {
		add(" <td>?</td>\n");
	    }
	    add("</tr>\n");
	}
	add("</table>\n");
    }
    add(DOW_HTML_Footer($Donor));
}
