#!/usr/bin/perl -w
#
# Enter a comment about a ship.
#

use strict;

use dow;

my($Donor, $Ship);

$Donor = ProcessDowCommandline();

if ($#ARGV != 0) {
    usage();
}

$Ship = $ARGV[0];
$Ship =~ s/\\//g;

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: entercomments.cgi?Ship");
}

sub GeneratePage {
    my($turn);

    if ($Donor->{label} =~ /^Anonymous/) {
	herror("No anonymous comments are allowed. Sorry.");
    }

    $turn = SelectOne("select max(turn) from turnupdate where donorid=?;",
		      $Donor->{donorid});
    add(DOW_HTML_Header($Donor, "$Donor->{ship}'s Comment About $Ship"));
    add("<h1>$Donor->{ship}'s Comment About $Ship</h1>");
    add("<a href=\"viewcomments.cgi?$Ship\">View Existing Comments</a><p><hr><p>\n");

    add("<form method=post action=\"commentsubmit.cgi\">\n");
    add("<input name=donorid type=hidden value=\"$Donor->{donorid}\">\n");
    add("<input name=ship type=hidden value=\"$Ship\">\n");
    add("What turn is this comment for? &nbsp; ");
    add("<input name=turn type=text size=20 value=\"" . ($turn-1) . "\"> &nbsp; &nbsp; (Must be a number. Use 0 if no particular turn is appropriate)<p>\n");

    add("Enter your comment below. Please include details such as if you were paired, where you were, etc. You may use html, but be careful! You can mess up viewing if you enter illegal html.");
    add("<p><textarea name=comment rows=6 cols=100></textarea>\n");

    add("<p>Enter your score for this encounter.");
    add("<p><select name=score>\n");
    add("<option value=1>1 - Best (gifted stuff)</option>");
    add("<option value=2>2 - Good</option>");
    add("<option value=3 selected>3 - Neutral</option>");
    add("<option value=4>4 - Poor</option>");
    add("<option value=5>5 - Worst (attacked)</option>");
    add("</select>\n");
    add("<p><hr><p><input type=submit> &nbsp; <input type=reset>\n");
    add("</form>");
    add(DOW_HTML_Footer($Donor));
}
