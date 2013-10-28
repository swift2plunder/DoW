#!/usr/bin/perl -w
#
# Completely clear a turn from dow2. Used only for debugging!
#
# Current settings will not cause a re-download.

use strict;
use Getopt::Std;
use dow2;

use vars qw($opt_t);

my($ArchivePath, $LogPath);

OpenDB("dow2");

$opt_t = SelectOne("select processturn from params;");
getopts('t:') or usage();

mydo("update params set processturn=?;", $opt_t);

$ArchivePath = SelectOne("select topdir from params;") . "/" . SelectOne("select archive from params;") . "/$opt_t";
$LogPath = SelectOne("select topdir from params;") . "/" . SelectOne("select logdir from params;") . "/$opt_t";

# Comment out one of the following.
#mydo("delete from downloadfiles where turn=?;", $opt_t);
ResetDownloads();

dd("activeships");
dd("flags");
dd("modules");
dd("pods");
dd("plagues");
dd("meetings");
dd("shiploc");
dd("trade");
dd("shippercents");

mydo("delete from curses where artifactid in (select artifactid from artifacts where turn=?);", $opt_t);
mydo("delete from keys where artifactid in (select artifactid from artifacts where turn=?);", $opt_t);
dd('artifacts');
dd('medicine');
dd('shipmisc');
dd('shared');

# Either remove everything, or just this turn
#system("rm -rf $ArchivePath");
#system("rm -rf $LogPath");

unlink("$LogPath/update.errors");
unlink("$LogPath/update.warnings");
unlink("$LogPath/update.messages");
CloseDB();

exit();

sub ResetDownloads {
    my($sth, $row);
    $sth = mydo("select * from downloadfiles where turn=? and status='Done';", $opt_t);
    while ($row = $sth->fetchrow_hashref()) {
	mydo("update downloadfiles set status='Traversed' where id=?;", $row->{id});
    }
    $sth->finish();
}

sub dd {
    my($table) = @_;
    mydo("delete from $table where turn=?;", $opt_t);
}
