#!/usr/bin/perl -w
######################################################################
#
# Lots of random stuff here that's used by other scripts.
#


use strict;
use DBI;
use POSIX;
use FileHandle;
use Time::Local;

my($MapFile, $TopDir, $TopURL);

$TopDir = '/Path/to/dow';
$TopURL = 'http://janin.org/dow';

$MapFile = "$TopDir/system.html";

my $DBH;
my $PageData;

#
# Forward to the file nodow.html and exit

sub NoDow {
    print<<EndOfNoDow;
Refresh: 0;URL=http://janin.org/dow/nodow.html
Content-type: text/html

<html>
<head>
<META HTTP-EQUIV="Refresh" CONTENT="0;URL=http://janin.org/dow/nodow.html">
<title>DOW</title>
</head>
<body>
You should automatically be forwarded to a message page at <a href="http://janin.org/dow/nodow.html">http://janin.org/dow/nodow.html</a>. If forwarding fails, click on the link.
</body>
</html>
EndOfNoDow

    exit(0);
}

# 
# 1). If the REMOTE_USER is not an admin, just return the donor
#     information for the remote user.
#
# 2). If the REMOTE_USER is an admin and "-u Ship" is given on the command
#     line, return the donor information for Ship and remove "-u Ship"
#     from ARGV. Used for debugging.
#
# 3). Log the access to the dowaccess table.
#

sub ProcessDowCommandline {
    my($ship, $donor, $i, $remote_user, $sth);
    if (-e "$TopDir/nodow.html") {
	NoDow();
    }

    # Open the database if necessary
    if (!defined($DBH)) {
	OpenDB();
    }

    # Check if access appears to be via web or via command line
    # Is there a better way to do this?
    
    if (!exists($ENV{REMOTE_USER})) {
	# Not web access. Probably command line debugging.
	# Just use me.
	$remote_user = 'Mad Ninja';
    } else {
	$remote_user = $ENV{REMOTE_USER};
	$remote_user =~ s/\\//g;	# Not sure who's adding backslash...
    }

    # Get donor info
    $sth = mydo("select * from donors where ship=?;", $remote_user);
    $donor = $sth->fetchrow_hashref();
    if (!defined($donor)) {
	herror("Couldn't get donor info for $remote_user");
    }
    $sth->finish();

    if (ExistsSelect("select * from frozen where ship=?;", $donor->{ship})) {
	herror("Your DOW account has been frozen, probably because you changed your secret URL and did not inform the admin of DOW. Please contact ninja\@janin.org.");
    }
    
    # Log if via web

    if (exists($ENV{REMOTE_USER})) {
	mydo("insert into dowaccess values(?, ?, ?, ?, ?, default, ?);",
	     $ENV{HTTP_USER_AGENT},
	     $remote_user,
	     $ENV{REMOTE_ADDR},
	     $ENV{REQUEST_URI},
	     $ENV{HTTP_REFERER},
	     SelectOne("select max(turn) from turnupdate where donorid=?;",
		       $donor->{donorid}));
    }

    # If -u arg given, remote it and set $ship to it.
    
    for ($i = 0; $i <= $#ARGV; $i++) {
	if ($ARGV[$i] eq '-u') {
	    $ship = $ARGV[$i+1];
	    splice(@ARGV, $i, 2);
	} elsif ($ARGV[$i] =~ /^-u\s*(.*?)\s*$/) {
	    $ship = $1;
	    splice(@ARGV, $i, 1);
	}
    }

    # If no -u, use remote user for ship
    if (!defined($ship)) {
	$ship = $remote_user;
    } else {
	# If admin, get donor info for -u
	if (!$donor->{admin}) {
	    herror("You must be an admin to use the -u option");
	}
	$ship =~ s/\\//g;
	$sth = mydo("select * from donors where ship=?;", $ship);
	$donor = $sth->fetchrow_hashref();
	if (!defined($donor)) {
	    herror("Couldn't get donor info for $remote_user");
	}
	$sth->finish();
    }

    return $donor;
} # ProcessDowCommandline

# Some routines used with the forums. These should probably be elsewhere.

sub ProcessForumCommandline {
    my($donor) = @_;
    my($forumdata, $forum, $i);
    $forum = 'general';
    for ($i = 0; $i <= $#ARGV; $i++) {
	if ($ARGV[$i] eq '-f') {
	    $forum = $ARGV[$i+1];
	    splice(@ARGV, $i, 2);
	}
    }
    ConfirmReadForum($donor, $forum);
    if (!ExistsSelect("select * from forumoptions where ship=? and forum=?;", 
		      $donor->{ship}, $forum)) {
	mydo("insert into forumoptions values(?, ?);", $donor->{ship}, $forum);
    }
    $forumdata = SelectOneRowAsHash("select * from forumoptions where ship=? and forum=?;", $donor->{ship}, $forum);
    return $forumdata;
}

# Check if given donor can read the given forum. Report an error
# if not. Return 1 if so.

sub ConfirmReadForum {
    my($donor, $forum) = @_;

    if (defined($donor) && $donor->{admin}) {
	return 1;
    }

    if ($forum eq "xeno" && (!defined($donor) || !$donor->{xeno})) {
	herror("You must be a member of the Institute of Xenology to read or post to the Institute of Xenology forum");
    } 

    if (!defined($donor)) {
	herror("You must be a member of DOW to read forum $forum");
    }
    
    if ($forum ne "general" && $forum ne "advice" && $forum ne "xeno") {
	herror("Illegal forum. Try \"general\".");
    }
    
    return 1;
}

# For now, anybody who can read can post.

sub ConfirmPostToForum {
    my($donor, $forum) = @_;
    return ConfirmReadForum($donor, $forum);
}

sub GetForumList {
    my($donor) = @_;
    my(@forums);
    if (defined($donor)) {
	push(@forums, 'general');
	if ($donor->{xeno}) {
	    push(@forums, 'xeno');
	}
	push(@forums, 'advice');
    }
    return @forums;
}    

#
# Check if there are any unread messages on the given
# forums. If no forums are passed, check all forums.
# 
# If delivery is email, always return false.
# If delivery is daily, return true if there are undelivered messages.
# If delivery is web, return true if you're not on the last page.
#
# The logic assumes that there are no skipped message ids (I think).

sub UnreadForumMessages {
    my($donor, @forums) = @_;
    my($sth, $row, $forumstr);
    if ($#forums < 0) {
	@forums = GetForumList($donor);
    }

    # First, check for web delivery

    $forumstr = "(" . join(' or ', map { "o.forum='$_'"} @forums) . ")";
    
    if (ExistsSelect("select o.forum from forumoptions o, forummessages m where o.delivery='web' and o.ship=? and $forumstr and o.forum=m.forum group by o.forum, o.last_read, o.msgs_per_page having count(*) >= o.last_read+msgs_per_page;", $donor->{ship})) {
	return 1;
    }

    if (ExistsSelect("select o.forum from forumoptions o, forummessages m, forumdaily d where o.delivery='daily' and o.ship=? and $forumstr and o.forum=m.forum and o.forum=d.forum group by o.forum, d.last_message having count(*) > d.last_message;", $donor->{ship})) {
	return 1;
    }
 
    return 0;
}

######################################################################
#
# Some routines to help with sorting
# This stuff is pretty ugly.
#
# Given a string and a hash of letters => field names,
# generate "order by foo, bar" instructions.
# The sorts hash should have all lowercase letters.

sub GenerateOrderBy {
    my($s, %sorts) = @_;
    my($i, @r, %r, $c, $lc);
    for ($i = 0; $i < length($s); $i++) {
	$c = substr($s, $i, 1);
	$lc = lc($c);
	next if (exists($r{$lc}));
	$r{$lc} = 1;
	if (exists($sorts{$lc})) {
	    if ($c eq $lc) {
		push(@r, $sorts{$lc});
	    } else {
		push(@r, "$sorts{$lc} desc");
	    }
	}
    }
    if ($#r >= 0) {
	return "order by " . join(", ", @r);
    } else {
	return '';
    }
}

sub GenerateSortArg {
    my($str, $c) = @_;
    my($s, $ls, $pos);
    $c = lc(substr($c, 0, 1));

    # If str starts with c, toggle the case
    $s = substr($str, 0, 1);
    $ls = lc($s);
    if ($ls eq $c) {
	if ($s eq $ls) {
	    substr($str, 0, 1) = uc($s);
	} else {
	    substr($str, 0, 1) = $ls;
	}
    } else {
	# Otherwise, move c to the front, preserving case.
	$pos = index($str, $c);
	if ($pos >= 0) {
	    substr($str, $pos, 1) = '';
	    $str = "$c$str";
	} else {
	    $pos = index($str, uc($c));
	    if ($pos >= 0) {
		substr($str, $pos, 1) = '';
		$str = uc($c) . $str;
	    }
	}
    }
    return $str;
}


# Given a tech name, return the level (e.g. primitive = 1)

sub TechNameToLevel {
    my($tn) = @_;
    my %tns = qw(primitive 1 basic 2 mediocre 3 advanced 4 exotic 5 magic 6);
    if (! exists($tns{lc($tn)})) {
	my_error("Unable to find tech level of tech name $tn");
    }
    return $tns{lc($tn)};
}

sub TechLevelToName {
    my($tl) = @_;
    my @tls = qw( Primitive Basic Mediocre Advanced Exotic Magic );
    if ($tl !~ /^\s*[123456]\s*$/) {
	my_error("Illegal tech level $tl");
    }
    return $tls[$tl-1];
}

sub TechRE {
    return "(primitive)|(basic)|(mediocre)|(advanced)|(exotic)|(magic)";
}

sub GetShopItemName {
    my($i) = @_;
    my @n = ('Warp Drive', 'Impulse Drive', 'Sensor', 'Cloak', 'Life Support', 'Sickbay', 'Shield', 'Ram', 'Gun', 'Disruptor', 'Laser', 'Missile', 'Drone', 'Fighter', 'Pod');
    return $n[$i-1];
}

sub GetShopItemType {
    my($item) = @_;
    if ($item =~ /^warp/i) {
	return 1;
    } elsif ($item =~ /^impulse/i) {
	return 2;
    } elsif ($item =~ /^sensor/i) {
	return 3;
    } elsif ($item =~ /^cloak/i) {
	return 4;
    } elsif ($item =~ /^life/i) {
	return 5;
    } elsif ($item =~ /^sickbay/i) {
	return 6;
    } elsif ($item =~ /^shield/i) {
	return 7;
    } elsif ($item =~ /^ram/i) {
	return 8;
    } elsif ($item =~ /^gun/i) {
	return 9;
    } elsif ($item =~ /^disruptor/i) {
	return 10;
    } elsif ($item =~ /^laser/i) {
	return 11;
    } elsif ($item =~ /^missile/i) {
	return 12;
    } elsif ($item =~ /^drone/i) {
	return 13;
    } elsif ($item =~ /^fighter/i) {
	return 14;
    } elsif ($item =~ /^pod/i) {
	return 15;
    } else {
	my_error("Unexpected shop item $item");
    }
}

sub OpenDB {
    $DBH = DBI->connect("DBI:Pg:dbname=dow", "USERNAME", "PASSWORD");
    if (!$DBH) {
	my_error("Couldn't open connection to database: $!");
    } else {
	return $DBH;
    }
}

sub CloseDB {
    $DBH->disconnect();
    $DBH = undef;
}

sub DBQuote {
    my($str) = @_;
    return $DBH->quote($str);
}

sub myprep {
    my($q) = @_;
    my($sth);
    $sth = $DBH->prepare($q) or my_error("Prepare failed for '$q': " . $DBH->errstr);
    return $sth;
}

sub myex {
    my($sth, @rest) = @_;
    $sth->execute(@rest) or my_error("Couldn't execute: " . $sth->errstr);
}

sub mydo {
    my($q, @rest) = @_;
    my($sth);
    # Simple debug...
    if (($q =~ tr/\?/\?/) != ($#rest+1)) {
	my_error("Possible illegal call to mydo. Mismatched argument count. '$q'");
    }
    $sth = myprep($q);
    myex($sth, @rest);
    return $sth;
}


# Return the next ID in a sequence.
# Assumes you've just inserted something.
# In MySQL, use $DBH->{'mysql_insertid'}
# In Postgresql use select currval($seq_id_seq)

sub GetSequence {
    my($seq) = @_;
    return SelectOne("select currval(?);", $seq . "_seq");
}

# Call the given argument using mydo.
# The select must match one and only one scalar in the database,
# which SelectOne will return. Otherwise, report an error.

sub SelectOne {
    my($q, @rest) = @_;
    my($sth, $row, $ret, $gotone);

    $gotone = 0;
    $sth = mydo($q, @rest);
    while ($row = $sth->fetchrow_arrayref()) {
	if ($gotone) {
	    my_error("SelectOne returned more than one row for query '$q'");
	}
	$gotone = 1;
	if ($#{$row} != 0) {
	    my_error("SelectOne returned more than one value for query '$q'");
	}
	$ret = $row->[0];
    }
    if (!$gotone) {
	my_error("SelectOne failed to match any values for query '$q' and values " . join(", ", @rest));
    }
    $sth->finish();
    return $ret;
}	

# Same as SelectOne, but return $default if no match

sub SelectOneDefault {
    my($q, $default, @rest) = @_;
    my($sth, $row, $ret, $gotone);

    $gotone = 0;
    $sth = mydo($q, @rest);
    while ($row = $sth->fetchrow_arrayref()) {
	if ($gotone) {
	    my_error("SelectOne returned more than one row for query '$q'");
	}
	$gotone = 1;
	if ($#{$row} != 0) {
	    my_error("SelectOne returned more than one value for query '$q'");
	}
	$ret = $row->[0];
    }
    $sth->finish();
    if ($gotone) {
	return $ret;
    } else {
	return $default;
    }	
}

# Call the given argument using mydo.
# The select must match one row in the database, which will
# be returned as a hashref. If the number of matches is not
# exactly one, report an error.

sub SelectOneRowAsHash {
    my($q, @rest) = @_;
    my($sth, $row, $ret);

    $sth = mydo($q, @rest);
    $ret = $sth->fetchrow_hashref();
    if (!defined($ret)) {
	my_error("SelectOneRowAsHash failed to match any values for query '$q', args: " . join(", ", @rest));
    }
    $row = $sth->fetchrow_hashref();
    if (defined($row)) {
	my_error("SelectOneRowAsHash matched more than one value for query '$q'");
    }
    $sth->finish();
    return $ret;
} # SelectOneRowAsHash

sub SelectOneRowAsHashDefault {
    my($q, $default, @rest) = @_;
    my($sth, $row, $ret);

    $sth = mydo($q, @rest);
    $ret = $sth->fetchrow_hashref();
    if (!defined($ret)) {
	$ret = $default;
    } else {
	$row = $sth->fetchrow_hashref();
	if (defined($row)) {
	    my_error("SelectOneRowAsHash matched more than one value for query '$q'");
	}
    }
    $sth->finish();
    return $ret;
} # SelectOneRowAsHashDefault


# Return true if the given select returns anything. False otherwise.

sub ExistsSelect {
    my($q, @rest) = @_;
    my($sth, $row);
    $sth = mydo($q, @rest);
    $row = $sth->fetchrow_hashref();
    $sth->finish();
    return defined($row);
}    


# Call the given argument using mydo.
# The select must have only one return value.
# SelectAll will return them as an array.

sub SelectAll {
    my($q, @rest) = @_;
    my($sth, $row, @ret, $gotone);
    $sth = mydo($q, @rest);
    while ($row = $sth->fetchrow_arrayref()) {
	if ($#{$row} != 0) {
	    my_error("SelectAll returned more than one value for query '$q'");
	}
	push(@ret, $row->[0]);
    }
    $sth->finish();
    return @ret;
}	

sub trim {
    my($str) = @_;
    $str =~ s/^\s+//;
    $str =~ s/\s+$//;
    return $str;
}

sub PrintPageData {
    print $PageData;
}

# Create an html table containing $ncols columns and as many rows as needed.
# Populate with the items. It does NOT include the <table> or </table> tags!

sub MakeHTMLTable {
    my($ncols, @items) = @_;
    my($col, $item, $ret, $nrows, $row);
    $nrows = ceil(($#items+1)/$ncols);
    $ret = " <tr>\n\n";
    $item = shift(@items);
    for ($col = 0; $col < $ncols; $col++) {
	last if (!defined($item));
	$ret .= "  <td valign=top>\n  <table>\n";
	for ($row = 0; $row < $nrows; $row++) {
	    $ret .= "    <tr><td>$item</td></tr>\n";
	    $item = shift(@items);
	    last if (!defined($item));
	}
	$ret .= "  </table>\n  </td>\n\n";
    }
    $ret .= " </tr>\n";
    return $ret;
}

sub add {
    $PageData .= join('', @_);
}

sub PageDataPrepend {
    $PageData = join('', @_) . $PageData;
}

# Need to check for legal names here...
sub CanonicalizeSystem {
    my($system) = @_;

    if ($system =~ /^\s*s\s*\#?\s*([0-9]+)/i) {
	$system = "Star \#$1";
    } elsif ($system =~ /^\s*star\s*\#?\s*([0-9]+)/i) {
	$system = "Star \#$1";
    } else {
	$system = ucfirst($system);
    }
    return $system;
}

sub UncanonicalizeSystem {
    my($system) = @_;
    $system =~ s/Star \#/S/;
    return $system;
}

# Check if a skill exists. If so, return the turn it was created.
# If not, return 0.

sub CheckForSkill {
    my($donorid, $area, $name) = @_;
    my($sth, $row, $turn);
    $sth = mydo("select turn from skills where donorid=? and area=? and name=?;",
		$donorid, $area, $name);
    $row = $sth->fetchrow_hashref();
    if (defined($row) && exists($row->{turn})) {
	$turn = $row->{turn};
	$row = $sth->fetchrow_hashref();
	if (defined($row)) {
	    my_error("Got more than one skill for donorid=$donorid $area $name");
	}
	$sth->finish();
	return $turn;
    } else {
	$sth->finish();
	return 0;
    }
}    

sub GetJumpCost {
    my($donorid, $turn, $sys1, $sys2) = @_;
    my($warp, $d);

    if ($sys1 =~ /Holiday/ || $sys2 =~ /Holiday/) {
	return 99999;
    }

    if (ExistsSelect("select distinct system1 from artifacts, keys, stargates where artifacts.artifactid=keys.artifactid and donorid=? and turn=? and system1=? and system2=? and keys.key=stargates.key;", $donorid, $turn, $sys1, $sys2)) {
	return 0;
    }

    $warp = SelectOne("select warppercent from shipdata where donorid=? and turn=?;", $donorid, $turn);
    if ($warp <= 0) {
	return 99999;
    }
    $d = SelectOne("select sqrt(((s1.x - s2.x) * (s1.x - s2.x) + (s1.y - s2.y) * (s1.y - s2.y))) from starcoords s1, starcoords s2 where s1.system=? and s2.system=?;", $sys1, $sys2);
    return int(exp(4*$d/log($warp))/200);
    
#    $dsq = SelectOne("select ((s1.x - s2.x) * (s1.x - s2.x) + (s1.y - s2.y) * (s1.y - s2.y)) from starcoords s1, starcoords s2 where s1.system=? and s2.system=?;", $sys1, $sys2);
#    add("(debug) donorid=$donorid turn=$turn sys1=$sys1 sys2=$sys2 warp=$warp dsq=$dsq<p>");
#    return int(0.001 + $dsq * 10 / $warp);
}

# Return the most recent system for the given ship
sub GetLatestShipLocation {
    my($ship) = @_;
    my($turn);

    $turn = SelectOne("select max(turn) from shiploc where ship=?;", $ship);
    return SelectOne("select system from shiploc where ship=? and turn=?;",
		     $ship, $turn);
}

######################################################################
#
# I've played around with all sorts of ways of generating
# maps, but I've never cleaned up the code. Sorry!
#

sub MakeMap {
    my($ship, $hi, $med) = @_;	# references to arrays
    my(@all, %im, $sys, $fh, $line, $ret);
    my($image, $system1, $system2, $shipsystem);

    @all = SelectAll("select system from starcoords;");
    foreach $sys (@all) {
	$im{$sys} = 'smallgray.gif';
    }
    foreach $sys (@{$med}) {
	$im{$sys} = 'biggreen.gif';
    }
    foreach $sys (@{$hi}) {
	$im{$sys} = 'bigred.gif';
#	$im{$sys} = 'plague.jpg';
    }
    if (defined($ship)) {
	$shipsystem = GetLatestShipLocation($ship);
    }
    
    $fh = new FileHandle($MapFile) or herror("Couldn't open mapfile $MapFile");
    while ($line = <$fh>) {
	chop($line);
	next if ($line eq "<html>");
	next if ($line eq "</html>");
	if ($line eq '</TR>' || $line eq '<TR ALIGN=CENTER>' || $line =~ m|^<TD COLSPAN=[0-9]+> </TD>$| || $line eq '<TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0>' || $line eq '</TABLE>') {
	    $ret .= "$line\n";
	} elsif ($line =~ m|<TD><IMG SRC=\"([^\"]+)\"></TD><TD COLSPAN=[0-9]+><a href=\"system.cgi\?([^\"]+)\">([^<]+)</a></TD><TD COLSPAN=[0-9]+> </TD>|) {
	    $image = $1;
	    $system1 = $2;
	    $system2 = $3;
	    $system1 = CanonicalizeSystem($system1);
	    $system2 = CanonicalizeSystem($system2);
	    if ($system1 ne $system2) {
		herror("System name mismatch! $system1 $system2");
	    }
	    if (! -e $im{$system1} || !defined($im{$system1})) {
		herror("Couldn't find match for $system1");
	    }
	    if (! exists($im{$system1})) {
		herror("Couldn't find $system1!");
	    }
	    $line =~ s/IMG SRC=\"$image\"/IMG SRC=\"$im{$system1}\"/;
	    if (defined($shipsystem) && ($system1 eq CanonicalizeSystem($shipsystem))) {
		$line =~ s|<a href|<a style=\"color:\#ff0000;text-decoration:none\" href|;
	    } else {
		$line =~ s|<a href|<a style=\"color:\#000000;text-decoration:none\" href|;
	    }

	    $ret .= "$line\n";
	} else {
	    herror("Unexpected line in system '$line'");
	}
    }
    $fh->close();
    return $ret;
}

# Takes 2n+1 arguments.
# First argument is the ship name (or undef). Used for highlighting
# current location.
# The rest of the arguments should be a reference to an array of system
# names and a file name containing the image to use.

sub MakeMapImage {
    my($ship, @args) = @_;
    my(%syshash, $sysref, $imagefn, $i, $sys);

    for ($i = 0; $i < $#args; $i+=2) {
	$sysref = $args[$i];
	$imagefn = $args[$i+1];
	foreach $sys (@{$sysref}) {
	    $syshash{$sys} = "<img src=\"$imagefn\">";
	}
    }
    return MakeMapGeneral($ship, \%syshash, "<img src=\"smallgray.gif\">");
} # MakeMapImage

sub MakeMapGeneralNew {
    my($ship, $syshash, $default) = @_;
    my($sth, $row, $y, @x, @sys, $xpos, $i, $ncols, $color, $shipsystem);
    my($sys, @ret);
    
    foreach $sys (SelectAll("select system from starcoords;")) {
	if (!exists($syshash->{$sys})) {
	    $syshash->{$sys} = $default;
	}
    }

    if (defined($ship)) {
	$shipsystem = UncanonicalizeSystem(GetLatestShipLocation($ship));
    }	
    
    $ncols = 66;
    push(@ret, "<table border=0 cellspacing=0 cellpadding=0>");
    push(@ret, "<tr>");
    for ($i = 0; $i <= $ncols; $i++) {
	push(@ret, "<td><font size=\"-1\">&nbsp;&nbsp;&nbsp;</font></td>");
    }
    push(@ret, "</tr>\n");
    $sth = mydo("select distinct x  from starcoords order by x;");
    while ($row = $sth->fetchrow_hashref()) {
	$y = $row->{x};
	@x = SelectAll("select y from starcoords where x=? order by y;", $y);
	@sys = SelectAll("select system from starcoords where x=? order by y;",
			 $y);
	push(@ret, "<tr>\n <td colspan=$x[0]></td>");
	$xpos = $x[0];
	push(@x, $ncols);
	for ($i = 1; $i <= $#x; $i++) {
	    $sys = UncanonicalizeSystem($sys[$i-1]);
	    if (defined($shipsystem) && $sys eq $shipsystem) {
		$color = "#ff0000";
	    } else {
		$color = "#000000";
	    }
	    push(@ret, " <td colspan=" . ($x[$i] - $xpos) . "><font size=\"0\"><a style=\"color:$color;text-decoration:none\" href=\"system.cgi?$sys\">$syshash->{$sys[$i-1]}&nbsp;$sys</a>&nbsp;&nbsp;</font></td>");
	    $xpos = $x[$i];
	}
	push(@ret, "</tr>\n");
    }
    $sth->finish();
    push(@ret, "</table>");

    return join("\n", @ret);
} # MakeMapGeneralNew


# Given a hash ref of system => html fragment, make a map with it.
# The last argument is what to use if nothing is provided in the syshash.

sub MakeMapGeneral {
    my($ship, $syshash, $default) = @_;

    my(@all, $sys, $fh, $line, $ret);
    my($image, $system1, $system2, $shipsystem);

    @all = SelectAll("select system from starcoords;");
    foreach $sys (@all) {
	if (!exists($syshash->{$sys})) {
	    $syshash->{$sys} = $default;
	}
    }

    if (defined($ship)) {
	$shipsystem = GetLatestShipLocation($ship);
    }
    
    $fh = new FileHandle($MapFile) or herror("Couldn't open mapfile $MapFile");
    while ($line = <$fh>) {
	chop($line);
	next if ($line eq "<html>");
	next if ($line eq "</html>");
	if ($line eq '</TR>' || $line eq '<TR ALIGN=CENTER>' || $line =~ m|^<TD COLSPAN=[0-9]+> </TD>$| || $line eq '<TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0>' || $line eq '</TABLE>') {
	    $ret .= "$line\n";
	} elsif ($line =~ m|<TD><IMG SRC=\"([^\"]+)\"></TD><TD COLSPAN=[0-9]+><a href=\"system.cgi\?([^\"]+)\">([^<]+)</a></TD><TD COLSPAN=[0-9]+> </TD>|) {
	    $image = $1;
	    $system1 = $2;
	    $system2 = $3;
	    $system1 = CanonicalizeSystem($system1);
	    $system2 = CanonicalizeSystem($system2);
	    if ($system1 ne $system2) {
		herror("System name mismatch! $system1 $system2");
	    }
	    if (!defined($syshash->{$system1})) {
		herror("Couldn't find match for $system1");
	    }
	    if (! exists($syshash->{$system1})) {
		herror("Couldn't find $system1!");
	    }
	    $line =~ s/<IMG SRC=\"$image\">/$syshash->{$system1}/;
	    if (defined($shipsystem) && ($system1 eq CanonicalizeSystem($shipsystem))) {
		$line =~ s|<a href|<a style=\"color:\#ff0000;text-decoration:none\" href|;
	    } else {
		$line =~ s|<a href|<a style=\"color:\#000000;text-decoration:none\" href|;
	    }
	    
	    $ret .= "$line\n";
	} else {
	    herror("Unexpected line in system '$line'");
	}
    }
    $fh->close();
    return $ret;
} # MakeMapGeneral


# Return the ship the given ship is paired with, or undef if none/unknown
sub PairedShip {
    my($ship, $turn, $usedonated) = @_;
    my($sth, $row);

    # Try matching ship1
    if ($usedonated) {
	$sth = mydo("select * from meetings where turn=? and ship1=? and donated=true;", $turn, $ship);
    } else {
	$sth = mydo("select * from meetings where turn=? and ship1=?;",
		    $turn, $ship);
    }
    $row = $sth->fetchrow_hashref();
    $sth->finish();
    if (defined($row) && exists($row->{ship2}) &&
	defined($row->{ship2}) && $row->{ship2} !~ /^\s*$/) {
	return $row->{ship2};
    }

    # Try matching ship2
    $sth = mydo("select * from meetings where turn=? and ship2=?;",
		$turn, $ship);
    $row = $sth->fetchrow_hashref();
    $sth->finish();
    if (defined($row) && exists($row->{ship1}) &&
	defined($row->{ship1}) && $row->{ship1} !~ /^\s*$/) {
	return $row->{ship1};
    }

    return undef;
} # PairedShip

# Return the race of the alien ship, or undef if its a player
sub RaceOfShip {
    my($ship) = @_;
    if ($ship =~ /^\s*((:?Ant)|(:?Beetle)|(:?Bird)|(:?Cat)|(:?Dog)|(:?Elf)|(:?Fish)|(:?Goblin)|(:?Groundhog)|(:?Hamster)|(:?Kangaroo)|(:?Lizard)|(:?Lobster)|(:?Monkey)|(:?Otter)|(:?Penguin)|(:?Pig)|(:?Pixie)|(:?Rabbit)|(:?Rat)|(:?Sloth)|(:?Snake)|(:?Spider)|(:?Squirrel)|(:?Tiger)|(:?Troll)|(:?Turtle)|(:?Vole)|(:?Wasp)|(:?Weasel)|(:?Worm)|(:?Zebra))\s*[0-9]+\s*$/) {
	return $1;
    } else {
	return undef;
    }
}


# Hack to convert between text and html encodings
# (e.g. &lt; <=> <)

sub QuoteHTML {
    my($str) = @_;
    $str =~ s/\&/\&amp;/g;
    $str =~ s/</\&lt;/g;
    $str =~ s/>/\&gt;/g;
    $str =~ s/\"/\&quot;/g;
    return $str;
}

sub UnquoteHTML {
    my($str) = @_;
    $str =~ s/\&quot;/\"/g;
    $str =~ s/\&gt;/>/g;
    $str =~ s/\&lt;/</g;
    $str =~ s/\&amp;/\&/g;
    return $str;
}	


# Given a min,max range, return a min,max range that is rounded for
# pleasing viewing.

sub GetRoundedRange {
    my($min, $max) = @_;
    my($range, $x, $val, $newmin, $newmax);
    $range = $max-$min;
    $x = POSIX::floor(log10($range));
    $val = 10**($x-1) * graph_findscale($range/(10**$x));
    $newmin = $val * (POSIX::floor($min/$val)-1);
    $newmax = $val * (POSIX::ceil($max/$val)+1);
    return ($newmin, $newmax);
}

sub graph_findscale {
    my($v) = @_;
    if ($v <= 1) {
	return 1;
    } elsif ($v <= 2) {
	return 2;
    } elsif ($v <= 5) {
	return 5;
    } elsif ($v <= 10) {
	return 10;
    } else {
	print STDERR "findscale failed with $v!\n";
	return 20;
    }
}
	
   


# Total hack - if it appears to be a web page, call herror.
# Otherwise, just call error and hope the caller defined it.

sub my_error {
    my($msg) = @_;
    if (exists($ENV{SERVER_NAME})) {
	herror($msg);
    } else {
	error($msg);
    }
}

sub herror {
    my($msg) = @_;
    print StandardHTMLHeader("Error in DOW Database Access");
    print <<"EndOfError";
<h1>Fatal Error in DOW Database Access</h1>
<p>A fatal error occurred while processing your data. The error message was:<p>
$msg
<p>
Sorry for the inconvenience.
</body>
</html>
EndOfError

  exit(0);
}    

sub StandardHTMLFooter {
    return<<"EndOfFooter";
<p>
<hr>
<font size=-1>Questions or comments to the DOW Forum <a href=\"$TopURL/forumread.cgi\">general</a> (or <href=\"mailto:ninja\@janin.org\">ninja\@janin.org</a>)</font>
</body>
</html>
EndOfFooter
}


sub DOW_HTML_Footer {
    my($donor) = @_;
    my($bottombar);

    if (defined($DBH) && defined($donor) && exists($donor->{donorid}) && 
	defined($donor->{donorid})) {
	$bottombar = SelectOne("select bottombar from prefs where donorid=?;", $donor->{donorid});
    }
    if (!defined($bottombar)) {
	$bottombar = "<a href=\"$TopURL/front.cgi\">DOW Top</a>";
    }

    return<<"EndOfFooter";
</td></tr></table></td></tr></table>
<p>
<hr>
$bottombar
<hr>
<font size=-1>Questions or comments to the <a href=\"$TopURL/forumread.cgi\">DOW General Forum</a>.</font>
</body>
</html>
EndOfFooter
}


sub StandardHTMLHeader {
    my($title, $base, $metatag) = @_;
    if (!defined($base)) {
	$base = "$TopURL/";
    }
    if (!defined($metatag)) {
	$metatag = "<meta name=\"ROBOTS\" content=\"NOINDEX,NOFOLLOW\">";
    }
    return <<"EndOfHeader";
Pragma: no-cache
Expires: -1
Content-type: text/html

<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<html>
<head>
<META http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">
$metatag
<base href=\"$base\">
<title>$title</title>
</head>
<body>
EndOfHeader
}


sub DOW_HTML_Header {
    my($donor, $title) = @_;
    my($str, $leftbar);
    $leftbar = GetLeftbar($donor);
    $str =<<"EndOfHeader";
Pragma: no-cache
Expires: -1
Content-type: text/html

<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<html>
<head>
<META http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">
<meta name=\"ROBOTS\" content=\"NOINDEX,NOFOLLOW\">
<base href=\"$TopURL/\">
<title>$title</title>
</head>
<body>
$leftbar

EndOfHeader
    return $str;
}

# Return a string with the leftbar
sub GetLeftbar {
    my($donor) = @_;
    my($prefrow, $leftbar, $leftbarwidth, $ship, $turn, $cursys, $cursysline);
    my($pairedline, $pairedship, $lastpairedline, $lastpairedship);
    my($poll, $forum, $xeno, $closedays);

    $closedays = daysUntil("10/1/2008");
    
    $poll = '';
    $forum = '';
    $xeno = '';
    $leftbarwidth = 150;
    $pairedline = '';
    $lastpairedline = '';
    $cursysline = '';
    $ship = '';
    $turn = SelectOne("select max(turn) from turnupdate;");

    if (defined($donor)) {
	$ship = $donor->{ship};
	$turn = SelectOne("select max(turn) from turnupdate where donorid=?", $donor->{donorid});

	# Put a * in poll if there are open polls not voted in

	if (ExistsSelect("select * from polls where open=true and not exists (select * from pollvotes where polls.pollid=pollvotes.pollid and donorid=?);", 
			 $donor->{donorid})) {
	    $poll = '<font size="0" color="#FF0000">*</font>&nbsp;';
	}

	# Put a * in forums if there are forums where you're not on the last page.

	if (UnreadForumMessages($donor)) {
	    $forum = '<font size="0" color="#FF0000">*</font>&nbsp;';
	}

	# Put a * in xeno line if they haven't performed a task in 10 turns.
	if ($donor->{xeno}) {
	    if  (!ExistsSelect("select * from xeno_history where ship=? and turn>?;",
			       $ship, $turn-15)) {
		$xeno = '<font size="+1" color="#FF0000"><blink>*&nbsp;*</blink></font>&nbsp;';
	    } elsif (!ExistsSelect("select * from xeno_history where ship=? and turn>?;",
				   $ship, $turn-10)) {
		$xeno = '<font size="0" color="#FF0000">*</font>&nbsp;';
	    } 
	}

	# Get where they are 

	$cursys = SelectOne("select system from shiploc where ship=? and turn=?;",
			    $ship, $turn);
	$cursysline = "<font size=\"-1\">At <a href=\"system.cgi?" . UncanonicalizeSystem($cursys) . "\">$cursys</a></font><br>\n";

	# Get prefs
	$prefrow = SelectOneRowAsHash("select * from prefs where donorid=?;", 
				      $donor->{donorid});
	if (defined($prefrow) && exists($prefrow->{leftbarwidth}) &&
	    defined($prefrow->{leftbarwidth}) && 
	    $prefrow->{leftbarwidth} =~ /^\s*[0-9]+\s*$/) {
	    $leftbarwidth = $prefrow->{leftbarwidth};
	}

	# Get who they're paired with
	$pairedship = PairedShip($ship, $turn);
	if (defined($pairedship)) {
	    $pairedline = "&nbsp;&nbsp;<a href=\"shipsummary.cgi?$pairedship\">$pairedship</a><br>";
	}
	$lastpairedship = PairedShip($ship, $turn-1);
	if (defined($lastpairedship) && !defined(RaceOfShip($lastpairedship))) {
	    $lastpairedline = "<br>Last turn, you paired with <a href=\"shipsummary.cgi?$lastpairedship\">$lastpairedship</a>. Please enter a <a href=\"entercomments.cgi?$lastpairedship\">comment</a>.<br>\n";
	}
    }
	
    $leftbar = <<"EndOfLeftBar";
<table cellpadding=5 width=\"100%\" border><tr valign=top><td width=$leftbarwidth>
<em><a href=\"shipsummary.cgi?$ship\">$ship</a></em>&nbsp; ($turn)<br>
$cursysline
<table width=$leftbarwidth>
<tr><td><font size=\"-1\">System</font></td>
    <td><font size=\"-1\"><a href=\"systems.cgi\">L</a>&nbsp; </font></td>
    <td><font size=\"-1\"><a href=\"systems.cgi?-m\">M</a></font></td></tr>
<tr><td><font size=\"-1\">Adventures&nbsp;</font></td>
    <td><font size=\"-1\"><a href=\"adventures.cgi\">L</a>&nbsp; </font></td>
    <td><font size=\"-1\"><a href=\"advmap.cgi\">M</a></font></td></tr>
<tr><td><font size=\"-1\">Plagues</font></td>
    <td><font size=\"-1\"><a href=\"plagues.cgi\">L</a>&nbsp; </font></td>
    <td><font size=\"-1\"><a href=\"plagues.cgi?-m\">M</a></font></td></tr>
<tr><td><font size=\"-1\">Rogues</font></td>
    <td><font size=\"-1\"><a href=\"rogues.cgi\">L</a>&nbsp; </font></td>
    <td><font size=\"-1\"><a href=\"roguemap.cgi\">M</a></font></td></tr>
<tr><td><font size=\"-1\">Aliens</font></td>
    <td><font size=\"-1\"><a href=\"aliens.cgi\">L</a>&nbsp; </font></td>
    <td><font size=\"-1\"><a href=\"alienmap.cgi\">M</a></font></td></tr>
<tr><td><font size=\"-1\">Starnets</font></td>
    <td><font size=\"-1\"><a href=\"terminals.cgi\">L</a>&nbsp; </font></td>
    <td><font size=\"-1\"><a href=\"terminals.cgi?-m\">M</a></font></td></tr>
<tr><td><font size=\"-1\">Out of Date</font></td>
    <td><font size=\"-1\"><a href=\"outofdate.cgi\">L</a>&nbsp; </font></td>
    <td><font size=\"-1\"><a href=\"outofdate.cgi?-m\">M</a></font></td></tr>
<tr><td><font size=\"-1\">Custom (<a href=\"customset.cgi\">set</a>)</font></td>
    <td><font size=\"-1\"><a href=\"customsetsubmit.cgi?-q\">L</a>&nbsp; </font></td>
    <td><font size=\"-1\"><a href=\"customsetsubmit.cgi?-q+-m\">M</a></font></td></tr>
<tr><td colspan=3><font size=\"-1\"><a href=\"locs.cgi\">Other Locations</a></font></td><td></td></tr>
</table>
<font size=\"-1\"><br>
<a href=\"front.cgi\">Front Page</a><br>
<a href=\"ms.cgi\">Membership Data</a><br>
<a href=\"criminals.cgi\">Alien Criminals</a><br>
<a href=\"allres.cgi\">Trade Resources</a><br>
<a href=\"searchshop.cgi\">Shop Data</a><br>
<a href=\"shipsummaries.cgi\">Ship Summaries</a><br>
$pairedline
<a href=\"tracking.cgi\">Ship Tracking</a>&nbsp;&nbsp(<a href=\"settracking.cgi\"><font size=\"-1\">set</font></a>)<br>

<a href=\"turnulator.cgi\">Turnulator</a><br>
<a href=\"turncache.cgi\">Previous Turns</a><br>
<a href=\"prefs.cgi\">View Preferences</a><br>
<a href=\"influenceships.cgi\">Influence by Ship</a><br>
<a href=\"influence.cgi\">All Influence Data</a><br>
$xeno<a href=\"xeno.cgi\">Xenologists</a><br>
<a href=\"cs.cgi\">Combat Simulator</a><br>
Route Sim <a href=\"rsset.cgi\"><font size=\"-1\">set</font></a> <a href=\"rsresults.cgi\"><font size=\"-1\">results</font></a><br>
$poll<a href=\"poll.cgi\">DOW Polls</a><br>
$forum<a href=\"forumread.cgi\">DOW Forums</a><br>
<a href=\"wiki/index.cgi\">DOW Wiki</a><br>
<a href=\"http://janin.org/ninja/tb\">Module Trade Board</a><br>
<a href=\"links.cgi\">Links to other pages</a><br>
$lastpairedline
<br>DOW closes in <blink>$closedays</blink> days.<br>
</font>
</td><td><table><tr><td>
EndOfLeftBar

     return $leftbar;
}

sub daysUntil {
    my ($date) = @_;

    my ($month,$day,$year) = split ('/',$date);
    $month--;

    # Get the future day in epoch days
    my $futureTime = timelocal(0,0,0,$day,$month,$year);
    my $futureDays = int($futureTime / (24*60*60));

    # Get the current time in epoch days
    my $currentDays = int(time / (24*60*60));
    
    return ($futureDays - $currentDays);
}


1;
