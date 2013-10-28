#!/usr/bin/perl -w
######################################################################
#
# Galaxion wrote the core code.
#
# Integration with DOW is a Total Kludge.
#


use strict;
use FileHandle;
use Getopt::Std;

use dow;

use vars qw($opt_a $opt_n $opt_t);

my $Donor = ProcessDowCommandline();
my @BattleTurns;
my $Turn;	# Lazy. This should be an arg to various routines.

$opt_n = 40;
$opt_t = SelectOne("select max(turn) from turnupdate;");
getopts('an:t:') or usage();
if ($opt_n <= 0) {
    $opt_n = 10000;
}

@BattleTurns = get_battle_turns();

#foreach $Turn (@BattleTurns) {
#    print "'$Turn'\n";
#}
#exit;

if (!$Donor->{shipconfig}) {
    herror("You must donate ship configurations to use the battle score calculator.");
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: battlescore.cgi?-a+-n+50+-t+1121<p>&nbsp;-a includes aliens in the listing<br>&nbsp;-n+n limits the display to n listings<br>&nbsp;-t+turn List starting at that turn");
}

sub strip_spaces {
    my($str) = @_;
    $str =~ s/^<BR>$//gm;
    $str =~ s/\s+/ /g;
    $str =~ s/> />/g;
    $str =~ s/ </</g;
    $str =~ s/^ //;
    $str =~ s/ $//;
    return $str;
}

sub get_ships {
    my ($battle, $prebattle) = @_;
    if ($battle !~ /<H2>([^<]+) attacks ([^<]+) in [^,]+ terrain, opening fire at \w+ range<\/H2>/i) {
	herror("Couldn't find ship names in battle report. You probably had no battle on turn $Turn.");
    }
    my ($name1, $name2) = ($1, $2);
    if ($name1 !~ /^[A-Z][a-z]+ \d+$/) {
	$name1 =~ s/ /_/g;
	$name1 =~ s/\'/@/g;
    }
    if ($prebattle !~ /<A NAME="?$name1"?><\/A><TABLE BORDER="?1"?>.*?<\/TABLE>/i) {
	herror("Couldn't find $name1 in prebattle turn");
    }
    my $ship1 = $&;
    if ($name2 !~ /^[A-Z][a-z]+ \d+$/) {
	$name2 =~ s/ /_/g;
	$name2 =~ s/\'/@/g;
    }
    if ($prebattle !~ /<A NAME="?$name2"?><\/A><TABLE BORDER="?1"?>.*?<\/TABLE>/i) {
	herror("Couldn't find $name2 in prebattle turn");
    }
    my $ship2 = $&;
    return ($ship1, $ship2);
}

sub get_power_rank {
    my ($player_info) = @_;
    my $power_rank = 0;
    while ($player_info->{'details'} =~ /<TR[^>]*><TD>([^-<\(]+(?:-\d+D?)?)( ?\(U\))?<\/TD><TD>([^<]+)<\/TD><TD>[^<]+<\/TD><TD>\d+<\/TD>(?:<\/TR>)?/ig) {
	my ($module, $broken, $tech) = ($1, $2, $3);
	if (defined($broken)) {
	} elsif ($module =~ /^[A-Z]/) {
	} elsif ($module =~ /D$/) {
	} elsif ($module =~ /^pod-/) {
	    $power_rank += $tech;
	} else {
	    $power_rank += TechNameToLevel($tech);
	}
    }
    $player_info->{'power_rank'} = $power_rank;
}

sub transfer_modules {
    my ($battle, $player1_info, $player2_info) = @_;
    if ($battle =~ /<BR>([^<]+) demands ([^<]+) and ([^<]+) offers it/ig) {
	my ($ship1, $module, $ship2) = ($1, $2, $3);
	if ($ship1 eq $player1_info->{'ship'} && $ship2 eq $player2_info->{'ship'}) {
	    if ($player2_info->{'details'} !~ s/(<TR ALIGN=CENTER><TD>\Q$module\E<\/TD><TD>[^<]*<\/TD><TD>[^<]*<\/TD><TD>[^<]*<\/TD><\/TR>)//i) {
		herror("Can't find $module on $player2_info->{'ship'}'s ship: '$player2_info->{'details'}'");
	    }
	    $module = $1;
	    if ($player1_info->{'details'} !~ s/(<TR ALIGN=CENTER>)/$module$1/i) {
		herror("Failed to add $module to $player1_info->{'ship'}'s ship");
	    }
	} elsif ($ship1 eq $player2_info->{'ship'} && $ship2 eq $player1_info->{'ship'}) {
	    if ($player1_info->{'details'} !~ s/(<TR ALIGN=CENTER><TD>\Q$module\E<\/TD><TD>[^<]*<\/TD><TD>[^<]*<\/TD><TD>[^<]*<\/TD><\/TR>)//i) {
#		herror("Can't find '$module' on p1 $player1_info->{'ship'}'s ship: '$player1_info->{'details'}'");
		herror("Can't find '$module' on $player1_info->{'ship'}'s ship");
	    }
	    # herror("This is a debugging message. Try again shortly.");
	    $module = $1;
	    if ($player2_info->{'details'} !~ s/(<TR ALIGN=CENTER>)/$module$1/i) {
		herror("Failed to add $module to $player2_info->{'ship'}'s ship");
	    }
	} else {
	    herror("Ships don't match battle record: $player1_info->{'ship'} and $player2_info->{'ship'} vs $ship1 and $ship2");
	}
    }
}

sub remove_modules {
    my ($player1_info, $player2_info, $battle) = @_;
    while ($battle =~ /<BR>$player1_info->{'ship'} is hit, ([^<\(]+)(?: ?\(U\))? is lost/ig) {
	my $module = $1;
	if ($player1_info->{'details'} !~ s/<TR[^>]*><TD>$module( ?\(U\))?<\/TD><TD>([^<]+)<\/TD><TD>[^<]+<\/TD><TD>\d+<\/TD>(?:<\/TR>)?//i) {
	    herror("Could not find $module on $player1_info->{'ship'}'s ship");
	}
	my ($broken, $tech) = ($1, $2);
	if ($module =~ /^[A-Z]/) {
	    $player2_info->{'score'} += 6;
	} elsif ($module =~ /^pod-/) {
	    $player2_info->{'score'} += $tech;
	} else {
	    $player2_info->{'score'} += TechNameToLevel($tech);
	}
    }
}

sub get_player_info {
    my ($ship) = @_;
    if ($ship !~ /<A NAME=\"?([^\">]+)\"?>/i) {
	herror("Could not find ship name $ship");
    }
    my $name = $1;
    $name =~ s/@/\'/g;
    $name =~ s/_/ /g;
    return {
	'ship' => $name,
	'details' => $ship,
	'score' => 0,
    };
}

sub add_html_score {
    my ($player1_info, $player2_info) = @_;
    add("<tr align=center><td>$player1_info->{'ship'}</td><td>$player1_info->{'power_rank'}</td><td>$player1_info->{'score'}</td><td>");
    if ($player1_info->{'power_rank'} == 0) {
	add("Infinite (", $player1_info->{'score'} * $player2_info->{'power_rank'}, " / 0^2 * 100)");
    } else {
	add(sprintf("%.1f", $player1_info->{'score'} * $player2_info->{'power_rank'} / $player1_info->{'power_rank'} ** 2 * 100));
    }
    add("</td></tr>\n");
}

sub add_results {
    my ($player1_info, $player2_info) = @_;
    add("<center><p><font size=\"+1\">Turn <a href=\"turncache.cgi?$Turn\">$Turn</a>, $player1_info->{ship} vs. $player2_info->{ship}</font>\n<p>");
    add("<table>\n<tr><th></th><th align=left>Starting Power Rank&nbsp;&nbsp;</th><th align=left>Raw Score&nbsp;&nbsp;</th><th align=left>Weighted Score</th></tr>\n");
    add_html_score($player1_info, $player2_info);
    add_html_score($player2_info, $player1_info);
    add("</table></center><p><hr>\n");
}

sub process_battle {
    my ($battle, $ship1, $ship2) = @_;
    my $player1_info = get_player_info($ship1);
    my $player2_info = get_player_info($ship2);
    get_power_rank($player1_info);
    get_power_rank($player2_info);
    transfer_modules($battle, $player1_info, $player2_info);
    remove_modules($player1_info, $player2_info, $battle);
    remove_modules($player2_info, $player1_info, $battle);
    add_results($player1_info, $player2_info);
}

sub GeneratePage {
    my($battle, $prebattle, $ship1, $ship2, $prevturn, $turn);

    add(DOW_HTML_Header($Donor, "Battle Scores for $Donor->{ship}"));
    add("<h1>Battle Scores for $Donor->{ship}</h1>\n");

    add("By default, battles with aliens are not shown and only the last 40 turns are included.<p>To include alien battles, use <a href=\"battlescore.cgi?-a\">http://janin.org/dow/battlescore.cgi?-a</a>.<p>To list a different number of turns (e.g. the last 200 turns), use <a href=\"battlescore.cgi?-n+200\">http://janin.org/dow/battlescore.cgi?-n+200</a>.<p>To list all battles in all turns, use <a href=\"battlescore.cgi?-a+-n+0\">http://janin.org/dow/battlescore.cgi?-a+-n+0</a>.\n");

    add("<p><hr><p>\n");

    foreach $turn (@BattleTurns) {
	$Turn = $turn;
	$prevturn = $turn - 1;
	$battle = get_file("/Path/to/turns/$Turn/$Donor->{donorid}.html");
	$prebattle = get_file("/Path/to/turns/$prevturn/$Donor->{donorid}.html");
	process_battle($battle, get_ships($battle, $prebattle));
    }

    add(DOW_HTML_Footer($Donor));
}

sub get_file {
    my($fn) = @_;
    my($fh, $content);
    $fh = new FileHandle($fn) or herror("Couldn't open turn file: $!");
    $content = join('', <$fh>);
    $content = strip_spaces($content);
    $fh->close();
    return $content;
}

sub get_battle_turns {
    my($fh, $line, @res, $turn);
    $fh = new FileHandle("grep -l '^<H3>Round 1, range is' /Path/to/turns/*/$Donor->{donorid}.html|") or herror("Couldn't open pipe: $!");
    while ($line = <$fh>) {
	if ($line =~ m|^/Path/to/turns/([0-9]+)/$Donor->{donorid}\.html$|) {
	    $turn = $1;
	    if ($turn > $opt_t-$opt_n && $turn <= $opt_t && 
		(defined($opt_a) || !defined(RaceOfShip(PairedShip($Donor->{ship}, $turn-1, 0))))) {
		push(@res, $turn);
	    }
	} else {
	    herror("Unexpected line from pipe: $line");
	}
    }
    $fh->close();
    @res = sort {$b <=> $a} @res;
    return @res;
}
