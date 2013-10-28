#!/usr/bin/perl -w
#
# Member Settings.
#
# Allows members to change their turn settings (e.g. secret URL,
# sharing, etc).
#
# The changes take effect at the very start of the next turn update.

use strict;

use dow;

my $Donor = ProcessDowCommandline();

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: membersettings.cgi");
}

sub GeneratePage {
    add(DOW_HTML_Header($Donor, "Membership Settings for $Donor->{ship}"));
    add("<h1>Membership Settings for $Donor->{ship}</h1>\n");
    add("<form method=post action=\"mssubmit.cgi\">\n");
    add("<input name=current_dow_pw type=hidden value=\"$Donor->{dow_pw}\">\n");
    add("<p>Changes to your settings take place during the next turn update. Please use with care!\n<p>");

    add("<hr><p><table border>\n");
    addinput("Secret URL", 'secreturl');
    addinput("DOW password", 'dow_pw');
    addinput("Email address", 'email');
    add("</table>\n");
    add("<p><table border>\n");
    addboolline("Do you want to be an anonymous member?", "anonymous");
    addboolline("Do you want DOW to automaticly obfuscate some of your data to help protect your anonymity?", "obfuscate");
    add("</table>\n");
    add("<p>You can only access data that you also share. Do you want to share:\n");
    add("<p><table border>\n");
    addboolline("Ship locations?", "shiploc");
    addboolline("Ship configurations?", "shipconfig");
    addboolline("Influence (i.e. presidential votes)?", "influence");
    addboolline("Information on terminal purgers <em>with the public</em>?", "purgers");
    addboolline("Primitive and Basic shop modules <em>with the public</em>?", "pub_shop_newbie");
    addboolline("Trade data <em>with the public</em>?", "pub_trade");
    add("</table>\n");
    add("<p>You can only see adventures of the same type as you share. Do you want to share:\n");
    add("<p><table border>\n");
    addboolline("All adventures?", "adv_all");
    addboolline("Level 1-5?", "adv_newbie");
    addboolline("Level 25-32?", "adv_hard");
    addboolline("Too high level for you to complete?", "adv_high");
    addboolline("Already done at least once (i.e. received the skill level)?", "adv_done");
    addboolline("Level 1-4 <em>with the public</em>?", "pub_adv_newbie");
    add("</table>\n");
    add("(Note: If you set \"All Adventures\" to \"Yes\", all the others EXCEPT newbie public adventures will be set to \"Yes\" automatically.)\n");
   
    add("<p><input type=submit> &nbsp; <input type=reset>\n");
    add("</form>\n");

    add(DOW_HTML_Footer($Donor));
}

sub addboolline {
    my($desc, $lab) = @_;
    my($selyes, $selno);

    if (exists($Donor->{$lab}) && defined($Donor->{$lab}) &&
	$Donor->{$lab}) {
	$selyes = ' selected';
	$selno = '';
    } else {
	$selyes = '';
	$selno = ' selected';
    }

    add("<tr><td>$desc</td>\n");
    add("<td><select name=$lab>");
    add("<option$selyes>Yes</option>\n");
    add("<option$selno>No</option></select></td>\n");
    add("</tr>\n");
}

sub addinput {
    my($desc, $lab) = @_;
    my($str);
    $str = QuoteHTML($Donor->{$lab});
    add("<tr><td>$desc</td><td><input name=$lab type=text value=\"$str\" size=50></td></tr>\n");
}

    
