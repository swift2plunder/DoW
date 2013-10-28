#!/usr/bin/perl -w
#
# Self-administered Xenologist Actions
#
# The turn is the turn reported on the turn page when the action is
# reported and completed, not the turn when the action is ordered.
#
#  BUG: Note hardwiring of path to detect if terminal report or probe
#  report was cast.
#
#

use strict;
use Getopt::Std;

use dow;

use vars qw($opt_t);

my($Donor);

if (exists($ENV{'CONTENT_LENGTH'})) {

    ProcessSubmit();

} else {

    $Donor = ProcessDowCommandline();
    if (!$Donor->{xeno}) {
	herror("This page is for Xenologists only");
    }

    $opt_t = SelectOne("select max(turn) from turnupdate;");
    getopts('t:') or usage();
    
    if ($#ARGV != -1) {
	usage();
    }

    GeneratePage();
}

PrintPageData();

CloseDB();

exit;

sub ProcessSubmit {
    my($buffer, @namevals, $nameval, $name, $value, %form);

    map { $form{$_} = undef; } qw (donorid dow_pw turn action);

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

	if (!exists($form{$name})) {
	    herror("Illegal form entry $name");
	}
	if (defined($form{$name})) {
	    herror("$name already defined");
	}
	$form{$name} = $value;
    }

    OpenDB();

    $Donor = SelectOneRowAsHash("select * from donors where donorid=? and dow_pw=?;", $form{donorid}, $form{dow_pw});
    if (!$Donor->{xeno}) {
	herror("This page is for Xenologists only");
    }
    $opt_t = $form{turn};

    if (!exists($form{action}) || !defined($form{action}) || 
	$form{action} =~ /^\s*$/ || $form{action} eq 'None') {
	$form{action} = "No action";
    } elsif ($form{action} ne AccessedTerminal() &&
	     $form{action} ne RFAT() &&
	     $form{action} ne ProbeReport() &&
	     $form{action} ne OutOfDate()) {
	herror("Unexpected action $form{action}");
    } else {
	mydo("insert into xeno_history values(default, ?, ?, ?);", $Donor->{ship},
	     $form{turn}, $form{action});
    }

    add("Refresh: 0;URL=http://janin.org/dow/xeno.cgi\n");
    add("Content-type: text/html\n\n");
    add("<html>\n<head>\n");
    add("<META HTTP-EQUIV=\"Refresh\" CONTENT=\"0;URL=http://janin.org/dow/xeno.cgi\">\n");
    add("<title>Xenologist Entry Added</title>\n");
    add("</head>\n");
    add("<body>\n");
    add("Xenology entry for $Donor->{ship} on turn $form{turn} added.<p>Action: $form{action}.<p>\n");
    add("You should be returned to the <a href=\"xeno.cgi\">Xenology</a> page shortly.\n");
    add("</body>\n");
    add("</html>\n");
}


sub usage {
    print STDERR "Usage: xenoself.pl";
    exit;
}

sub GeneratePage {
    my($gotone, $ret, $sth, $row, $action, @options);
    add(DOW_HTML_Header($Donor, "Institute of Xenology Self Administration"));
    add("<h1>Institute of Xenology Self Administration</h1>");
    add("<p>This page lists the actions that you took on your last turn that may count as a service for the Institute of Xenology. The intention is for members to use this when they perform a service for the Institute. You should not simply check this page every turn, and submit when you coincidently performed a service the previous turn.\n");
    add("<p>Pick an action below and select <em>Submit</em> to record your service. If you performed a valid service, but it doesn't appear in the list below, you should email <a href=\"mailto:ninja\@janin.org\">ninja\@janin.org</a> instead.\n");

    add("<p>");
    $sth = mydo("select * from xeno_history where ship=? and turn=?;",
		$Donor->{ship}, $opt_t);
    $row = $sth->fetchrow_hashref();
    if (defined($row) || exists($row->{action})) {
	$action = $row->{action};
	add("<font size=\"+2\" color=\"#ff7777\">Note: You have already been credited with the action \"$action\" on turn $row->{turn}.</font><p>\n");
	$gotone = 1;
    } else {
	# Kludge alert!
	$action = "A random string that shouldn't match a valid action.";
	$gotone = 0;
    }
    $sth->finish();

    if (defined($ret = AccessedTerminal()) && $ret ne $action) {
	push(@options, $ret);
    }

    if (defined($ret = RFAT()) && $ret ne $action) {
	push(@options, $ret);
    }

    if (defined($ret = ProbeReport()) && $ret ne $action) {
	push(@options, $ret);
    }

    if (defined($ret = OutOfDate()) && $ret ne $action) {
	push(@options, $ret);
    }

    if ($#options >= 0) {
	push(@options, "None");
	add("<form method=post action=\"xenoself.cgi\">\n");
	add("<input name=donorid type=hidden value=\"$Donor->{donorid}\">\n");
	add("<input name=dow_pw type=hidden value=\"$Donor->{dow_pw}\">\n");
	add("<input name=turn type=hidden value=\"$opt_t\">\n");
	add("<select name=action size=" . ($#options+1) . ">\n");
	add(map { " <option value=\"$_\">$_</option>\n" } @options);
	add("</select>\n<p><input type=submit> &nbsp; <input type=reset>\n");
	add("</form>\n");
    } elsif ($gotone) {
	add("No other Institute of Xenology services found on turn $opt_t.\n");
    } else {
	add("No Institute of Xenology services found on turn $opt_t.\n");
    }

    add("<p><hr><p>Actions that are listed here include accessing a terminal (if you have under 10 accesses already), casting Report from All Terminals (if you have 20 or more terminals accessed), casting Report from Probe on an out of date system, jumping to an out of date trade world (if the data is more than 2 turns out of date), or jumping to an out of date system (if your sensors are higher than 40%).<p>\n");
    add(DOW_HTML_Footer($Donor));
}

sub OutOfDate {
    my($system, $lastvisit, $lasttrade);

    $system = SelectOne("select system from shiploc where turn=? and ship=?;",
			$opt_t, $Donor->{ship});

    return undef if $system eq "Holiday Planet";

    $lastvisit = SelectOne("select max(turn) from shiploc, donors where system=? and shiploc.ship=donors.ship and turn<?;", $system, $opt_t);
    if (ExistsSelect("select * from trade where system=? limit 1;", $system)) {
	$lasttrade = SelectOne("select max(turn) from trade where system=? and turn<?;", $system, $opt_t);
    } else {
	# Kludge alert. Just set it high so tests always fail.
	$lasttrade = $opt_t + 1000;
    }    

    if ((SelectOne("select sensorpercent from shipdata where turn=? and donorid=?;", $opt_t, $Donor->{donorid}) >= 40 && $lastvisit <= $opt_t-10) ||
	($lasttrade <= $opt_t-2)) {
	return "Jumped to out of date $system";
    }
    return undef;
}

sub AccessedTerminal {
    my($sth, $row);
    # If 10 or fewer terminals, then terminal access is valid.
    if (SelectOne("select count(*) from terminals where turn=? and donorid=?;", 
		  $opt_t, $Donor->{donorid}) <= 10) {
	$sth = mydo("select system from terminals where donorid=? and turn=? and system not in (select system from terminals where donorid=? and turn=?);",
		    $Donor->{donorid}, $opt_t, $Donor->{donorid}, $opt_t-1);
	while ($row = $sth->fetchrow_hashref()) {
	    if (defined($row->{system})) {
		return "Accessed Terminal at $row->{system}";
	    }
	}
	$sth->finish();
    }
    return undef;
}


sub RFAT {
    # If 20 or more terminals access, then RFAT is legal
    if (SelectOne("select count(*) from terminals where turn=? and donorid=?;", 
		  $opt_t, $Donor->{donorid}) >= 20 && 
	-e "/Path/to/turns/$opt_t/$Donor->{donorid}.tr.html") {
	return "Cast RFAT";
    }
    return undef;
}

# ProbeReport should probably only give credit if out of date...
# Hardwired search in the turn page is also a bit dicey.

sub ProbeReport {
    my($ret);
    # fgrep is probably faster than anything perl can do
    $ret = `fgrep -l '<P>Probe report requested, see below for details' "/Path/to/turns/$opt_t/$Donor->{donorid}.html"`;
    if ($ret eq "/Path/to/turns/$opt_t/$Donor->{donorid}.html\n") {
	return "Cast Report from Probe";
    } else {
	return undef;
    }
}
