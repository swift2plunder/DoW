#!/usr/bin/perl -w
#
# Institute of Xenology, delete history entry
#

use strict;

use dow;

my($Donor, $ID);
$Donor = ProcessDowCommandline();

if (!$Donor->{xenoadmin}) {
    herror("Only the admin may delete Xenologist entries");
}

if ($#ARGV != 0) {
    usage();
}

$ID = $ARGV[0];

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: xeno_delete.cgi?ID");
}

sub GeneratePage {
    add("Refresh: 0;URL=http://janin.org/dow/xeno_admin.cgi\n");
    add("Content-type: text/html\n\n");
    add("<html>\n<head>\n");
    add("<META HTTP-EQUIV=\"Refresh\" CONTENT=\"0;URL=http://janin.org/dow/xeno_admin.cgi\">\n");
    add("<title>Xenologist Entry Deleted</title>\n");
    add("</head>\n");
    add("<body>\n");
    add("Xenologist entry id $ID deleted. You should be returned to the <a href=\"xeno_admin.cgi\">Xenology Administration</a> page shortly.\n");
    add("</body>\n");
    add("</html>\n");
    mydo("delete from xeno_history where id=?;", $ID);
}

