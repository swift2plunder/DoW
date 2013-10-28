#!/usr/bin/perl -w
#
# Experimental page to process form data from sharing.cgi
#

use strict;
use dow2;
use CGI;

my($Data);

MakePage();
PrintPageData();

CloseDB();

exit;

sub MakePage {
    my($query, $ship, $password, $sth, $row, $val, $turn, $id, $did, $sship);
    $query = new CGI;
    $ship = $query->param('ship');
    $password = $query->param('password');
    $Data = GetDowDataPW($ship, $password);
    $turn = $Data->{turn};
    AddDowHeader($Data,
		 {
		     title => 'Sharing Settings Submitted'
		     });
    add("<h1>Sharing Settings for $ship Submitted</h1>\n");
    add("<p>Changes will not take effect until the next turn update.</p>\n");

    # Delete any existing entries for this turn.
    mydo("delete from sharingships where id in (select id from sharingsettings where turn=? and ship=?);", $turn, $ship);
    mydo("delete from sharingsettings where turn=? and ship=?;", $turn, $ship);
    # Insert the default info
    mydo("insert into sharingsettings (ship, turn) values (?, ?);", $ship, $turn);
    $id = GetSequence("sharingsettings_id");
    SetSharing($ship, $turn, $id, $query, 'default');
    $sth = mydo("select * from sharingtypes;");
    while ($row = $sth->fetchrow_hashref()) {
	$val = $query->param("$row->{shortname}_default");
	if (defined($val) && $val eq "on") {
	    mydo("insert into sharingsettings (ship, turn, sharetypeid, usedefault) values (?, ?, ?, true);", $ship, $turn, $row->{sharetypeid});
	} else {
	    mydo("insert into sharingsettings (ship, turn, sharetypeid, usedefault) values (?, ?, ?, false);", $ship, $turn, $row->{sharetypeid});
	    $id = GetSequence("sharingsettings_id");
	    SetSharing($ship, $turn, $id, $query, $row->{shortname});
	}
    }
    $sth->finish();
    # Now add the default sharingships to the settings that have usedefault=true.
    $sth = mydo("select * from sharingsettings where ship=? and turn=? and usedefault=true and sharetypeid is not null;", $ship, $turn);
    $did = SelectOne("select id from sharingsettings where ship=? and turn=? and sharetypeid is null;", $ship, $turn);
    while ($row = $sth->fetchrow_hashref()) {
	foreach $sship (SelectAll("select ship from sharingships where id=$did;")) {
	    mydo("insert into sharingships(id, ship) values (?, ?);",
		 $row->{id}, $sship);
	}
    }
    $sth->finish();
    AddDowFooter($Data);
}

sub SetSharing {
    my($ship, $turn, $id, $query, $tag) = @_;
    my(@sids, $sid);

    # Extract out just the ship ids.
    @sids = map { $_ =~ /^${tag}_([0-9]+)$/; $1; } (grep { $_ =~ /^${tag}_[0-9]+$/ } $query->param);

    foreach $sid (@sids) {
	mydo("insert into sharingships (id, ship) values ($id, ?);",
	     SelectOne("select ship from activeships where turn=$turn and id=$sid;"));
    }    
}
    
    




#  "ship=Mad+Ninja&password=0nm.40wUNq8QM&shareradio=shiploc&default_184=on&default_118=on
#   &shipconfig_default=on&shiploc_98=on&shiploc_185=on"

