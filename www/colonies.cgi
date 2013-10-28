#!/usr/bin/perl -w
#
# Show info on colonies.
# If passed a system name, list all colonies in that system.
# If passed a resource name, list all colonies buying that good.
#

use strict;

use dow;

my($Donor, $SystemOrResource);

$Donor = ProcessDowCommandline();

if ($#ARGV != 0) {
    usage();
}

$SystemOrResource = shift;
$SystemOrResource =~ s/\\//g;

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: colonies.cgi?{Resource|System}");
}

sub GeneratePage {
    my(@colonies, $colony, $data);
    # See if it's a resource
    @colonies = SelectAll("select id from colonies where resource=?;", $SystemOrResource);
    if ($#colonies == -1) {
	$SystemOrResource = CanonicalizeSystem($SystemOrResource);
	@colonies = SelectAll("select id from colonies where system=?;", 
			      $SystemOrResource);
	if ($#colonies == -1) {
	    herror("No such system or resource '$SystemOrResource'");
	}
    }
    add(DOW_HTML_Header($Donor, "DOW Colony Information for $SystemOrResource"));
    add("<h1>Colony Information for $SystemOrResource</h1>\n");
    add("<table>");
    add("<tr><th align=left>System</th><th align=left>Race</th><th align=left>Resource</th></tr>\n");
    foreach $colony (@colonies) {
	$data = SelectOneRowAsHash("select * from colonies where id=?;", $colony);
	add("<tr><td><a href=\"system.cgi?" . UncanonicalizeSystem($data->{system}) . "\">$data->{system}</a>&nbsp;&nbsp;&nbsp;</td><td>$data->{race}&nbsp;&nbsp;&nbsp;</td><td><a href=\"res.cgi?$data->{resource}\">$data->{resource}</a></td><tr>\n");
    }
    add("</table>\n");
    add(DOW_HTML_Footer($Donor));
}

