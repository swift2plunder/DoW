#!/usr/bin/perl -w

use strict;

use dow;

my $MailExec = '/usr/lib/sendmail';

OpenDB();

my $Turn = SelectOne("select max(turn) from turnupdate;");

# Check if we've already sent two or more this turn. If so, just
# print a message and exit.

if (SelectOne("select count(*) from rfat where turn=?;", $Turn) < 2) {
    RFAT();
} else {
    print "RFAT requests already sent on turn $Turn.\n";
}

CloseDB();

sub RFAT {
    my($sth, $row, $rfat, $count);
    
    # The score for each ship is 5 * (the sum of the number of turns since
    # a trade world's prices were last updated) + number of terminals
    # accessed. The idea is to keep trade updated with high priority, but
    # also give some weight to ships with lots of accesses (e.g. to get
    # ship data).

    $sth = mydo("select t.ship, (t.score+a.score) as score from (select d.ship, 5*sum($Turn-lastupdate) as score from terminals t, donors d, (select system, max(turn) as lastupdate from trade group by system) l where t.donorid=d.donorid and t.system=l.system and turn=$Turn group by d.ship) t, (select ship, count(*) as score from terminals t, donors d where t.donorid=d.donorid and turn=$Turn group by ship) a where a.ship=t.ship and a.score > 10 order by 2 desc;");

    $count = 0;
    while ($row = $sth->fetchrow_hashref()) {
	# Skip if the ship has requested not to participate, or if they've
	# been requested within the last 5 turns.

	$rfat = SelectOneRowAsHashDefault("select * from rfat where ship=?;",
					  { ship => $row->{ship}, 
					    contact => 1,
					    turn => -1 },
					  $row->{ship});
	next if (!$rfat->{contact});
	next if ($rfat->{turn} > $Turn-5);
	next if (ExistsSelect("select system from shiploc where ship=? and turn=? and system='Holiday Planet';", $row->{ship}, $Turn));
	next if (SelectOne("select favour from favour f, donors d where f.donorid=d.donorid and turn=? and area='Science' and ship=?;", $Turn, $row->{ship}) < 100);
	mail_rfat($row->{ship});
	mydo("delete from rfat where ship=?;", $row->{ship});
	mydo("insert into rfat values(?, true, ?);", $row->{ship}, $Turn);
	last if $count++ >= 0;
    }
}

sub mail_rfat {
    my($ship) = @_;
    my($msg, $email);
    $email = SelectOne("select email from donors where ship=?;", $ship);
    $msg = <<"EndOfMessage";
From: ninja\@janin.org
To: $ship <$email>
Subject: [TBG] RFAT?

$ship,

You are receiving this message because you are a member of DOW and
have accessed a number of out of date Starnet terminals. In order
to keep DOW as up to date as possible, members such as yourself are
periodically requested to cast the Science spell 'Report from All
Terminals' (RFAT). This is a voluntary service! If you don't have
enough favour, or you're busy doing something else, or you just don't
want to participate, feel free to ignore this message.

If you do not wish to receive RFAT requests in the future, please send
email to ninja\@janin.org and I will remove you from the rotation.

If you are a member of the Institute of Xenology, and you would
like Institute of Xenology credit for casting RFAT, please just
use the Institute of Xenology "self administration" page at
http://janin.org/dow/xenoself.cgi on the turn after you cast. It
should show up there.

This is an automated message. There is no need to reply to it.

     Thanks!

     Adam Janin
     Captain of "A Mad Ninja" and DOW Admin
     ninja\@janin.org
     http://janin.org/ninja
EndOfMessage
    if (!open(MFD, "|$MailExec $email")) {
	print STDERR "Failed to open mail process\n";
	exit;
    }
    print MFD $msg;
    print "Mail sent to $ship <$email>\n";
    close(MFD);
}
