#!/usr/bin/perl -w
######################################################################
#
# Experimental "custom" score page using javascript.
#


use strict;

use LWP::Simple;	# For downloading orders

use dow;

my($Donor, $Turn, %Sys2Expr, %Sys2Index, @SystemNames, @FormElems, @Settings);

$Donor = ProcessDowCommandline();

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: customjs.cgi<br>\n");
}

sub GeneratePage {
    my(%sys2html, $sys, $sindex);
    my($cursys);
    $Turn = SelectOne("select max(turn) from turnupdate;");

    # Build up the data structures that describe the scores.

    $cursys = SelectOne("select system from shiploc where turn=? and ship=?;",
			$Turn, $Donor->{ship});
    $sindex = 0;
    @SystemNames = SelectAll("select system from starcoords");
    foreach $sys (@SystemNames) {
	$sys2html{$sys} = "<img border=none id=\"s$sindex\" src=\"biggray.gif\" width=8 height=8>";
	$Sys2Expr{$sys} = "settings[0] * " . GetJumpCost($Donor->{donorid}, $Turn, $cursys, $sys);
	$Sys2Index{$sys} = $sindex;
	$sindex++;	
    }

    push(@Settings, "jumpcost");

    # Here's the meat. Each line should have a unique id, a label for the
    # form, and a sql query that returns a list of systems.

    ScoreSystem('sn', "StarNet", 
		"select system from sysstarnet;");

    ScoreSystem('usn', "Unaccessed StarNet", 
		"select system from sysstarnet where system not in (select system from terminals where turn=? and donorid=?);", 
		$Turn, $Donor->{donorid});

    ScoreSystem('hh', "Hiring Hall", "select distinct system from statics where item=?;",'Hiring Hall');

    ScoreSystem('prison', "Prison",
		"select distinct system from statics where item=?;",
		"Prison");

    ScoreSystem('ocean', "Ocean",
		"select distinct system from statics where item=?;",
		"Ocean");

    ScoreSystem('hw', "Homeworld", "select system from aliens;");

    ScoreSystem('hwup', "Uncured Plague", "select system from aliens where system not in (select system from plagues where turn=? and donorid=?);", $Turn, $Donor->{donorid});
    
    ScoreSystem('hwne', "Not an Enemy", "select system from aliens where race not in (select who from enemies where turn=? and donorid=?);", $Turn, $Donor->{donorid});

    ScoreSystem('hwh', "Hostile Homeworld",
		"select system from aliens where alignment='Hostile';");
    
    ScoreSystem('hwc', "Chaotic Homeworld",
		"select system from aliens where alignment='Chaotic';");
    
    ScoreSystem('factory', "Factory", "select system from factories;");

    ScoreSystem('cfactory', "Contraband Factory", "select system from factories where resource like '%!%';");

    
    DoResource();

    
    # 4 entries per call (Engineering, Science, Medical, Weaponry)

    ScoreSystemAreas('acad', "Academies", 
		     "select distinct system from statics where item='%area Academy';");

    ScoreSystemAreas('school', 'Schools', 
		     "select distinct system from statics where item='%area School';");

    ScoreSystemAreas('rogue', 'Rogue Bands', 
     sprintf("select distinct system from rogues where field='%%area' and turn=$Turn and ((location='Impulse' and danger<=%d) or (location='Life Support' and danger<=%d));",
	     SelectOne("select impulsepercent from shipdata where donorid=? and turn=?;", $Donor->{donorid}, $Turn),
	     SelectOne("select lifesupportpercent from shipdata where donorid=? and turn=?;", $Donor->{donorid}, $Turn)));


    DoAdventures();


    add_header();

    add("<div id=divmap>\n");
    add(MakeMapGeneralNew($Donor->{ship}, \%sys2html, "ERROR"));
    add("</div>\n");
    add("<div id=divsettings>\n");
    add("<form name=\"settingsform\" onsubmit=\"return false;\">\n");
    add("<table>\n");
    add("<tr><td>Jump Cost</td><td>");
    add("<input name=jumpcost size=4></td></tr>\n");
    add(join("\n", @FormElems));
    add("</table>\n");
    add("<button onclick=\"updateSizes()\" type=button>Update</button>\n");
    add("</form>\n");
    add("</div>\n");
    add("</body></html>\n");
}

sub DoAdventures {
    my($sth, $row, @reqs, $req, $qadv, $quadv);
    my($prefadvmin, $prefadvmax);

    # Get the latest ship levels
    $sth = mydo("select * from shipdata where donorid=? and turn=(select max(turn) from shipdata where donorid=?);", $Donor->{donorid}, $Donor->{donorid});
    $row = $sth->fetchrow_hashref();
    if (!defined($row)) {
	herror("Couldn't get ship data");
    }
    $sth->finish();

    $qadv = "select distinct system from adventures where area='%area' and turn=? and ((area='Engineering' and level<=$row->{engskill}) or (area='Science' and level<=$row->{sciskill}) or (area='Medical' and level<=$row->{medskill}) or (area='Weaponry' and level<=$row->{weapskill})) and (";

    @reqs = ();
    if ($Donor->{donorid} == 1) {
	@reqs = 'true';
    } else {
	foreach $req (qw(adv_all adv_newbie adv_done adv_high adv_hard)) {
	    if ($Donor->{$req}) {
		push(@reqs, "$req=true");
	    }
	}
	$sth->finish();
    }
    if ($#reqs == -1) {
	return;
    }

    $qadv .= join(' or ', @reqs) . ")";
    $quadv = "$qadv and name not in (select distinct name from skills where donorid=? and skills.area=adventures.area)";
    
    ScoreSystemAreas('adv', "Adventures", "$qadv;", $Turn);

    ScoreSystemAreas('uadv', "Uncompleted Adventures", "$quadv;",
		     $Turn, $Donor->{donorid});

    $prefadvmin = SelectOne("select prefadvmin from prefs where donorid=?",
			    $Donor->{donorid});
    $prefadvmax = SelectOne("select prefadvmax from prefs where donorid=?",
			    $Donor->{donorid});
    if (!defined($prefadvmin)) {
	$prefadvmin = 0;
    }
    if (!defined($prefadvmax)) {
	$prefadvmax = 32;
    }

    ScoreSystemAreas('padv', "Preferred Adventures", "$qadv and level>=$prefadvmin and level<=$prefadvmax;", $Turn);

} # DoAdventures


sub DoResource {
    my($sth, $row, $ssth, $srow, $str);
    my(%res);        # Resource name => amount of resource
    my(@res);	     # set to keys(%res)
    my(%sys2value);	# System => total value of meds and resources.
    my(%sys2profit);	# System => total value minus cost to buy
    my(%cost);       # Resource => cost to buy at factory
    my($res, $sys, $resindex, $profitindex);

    push(@Settings, 'res');
    push(@FormElems, "<tr><td>Trade Value</td><td><input name=res size=4></td></tr>");
    $resindex = $#Settings;
    
    push(@Settings, 'profit');
    push(@FormElems, "<tr><td>Trade Profit</td><td><input name=profit size=4></td></tr>");
    $profitindex = $#Settings;

    # Medicine

    $sth = mydo("select * from medicine where ship=? and turn=?;", $Donor->{ship}, $Turn);
    $row = $sth->fetchrow_hashref();
    if (defined($row) && exists($row->{system}) && defined($row->{system})) {
	$sys2value{$row->{system}} = $row->{value};
	$sys2profit{$row->{system}} = $row->{value};
    }

    $sth->finish();

    # Trade resources. The join with factories is to exclude Empty
    # and mercs and to extract prices.

    $sth = mydo("select pods.resource, sum(n), cost from pods, factories where pods.resource=factories.resource and donorid=? and turn=? and n>0 group by pods.resource, cost;", $Donor->{donorid}, $Turn);
    while ($row = $sth->fetchrow_hashref()) {
	$res{$row->{resource}} = $row->{sum};
	$cost{$row->{resource}} = $row->{cost};
    }
    $sth->finish();

    # Process orders, if any, here. Disabled currently because it's too slow.
    # This should be a command line argument.
    # ProcessOrders(\%res);
    
    @res = keys(%res);
    if ($#res >= 0) {

	$str = "select distinct system, max(turn) from trade where resource in ('" . join("', '", map { s/\'/\\\'/g; $_; } @res) . "') group by system ;";

	$ssth = mydo($str);
    
	while ($srow = $ssth->fetchrow_hashref()) {
	    foreach $res (@res) {
		$res =~ s/\\//g;
		$sth = mydo("select * from trade where system=? and turn=? and resource=? limit $res{$res};", $srow->{system}, $srow->{max}, $res);
		while ($row = $sth->fetchrow_hashref()) {
		    $sys2value{$srow->{system}} += $row->{price};
		    $sys2profit{$srow->{system}} += $row->{price} - $cost{$res};
		}
		$sth->finish();
	    }
	}
	$ssth->finish();
    }
    foreach $sys (keys %sys2value) {
	print STDERR "processing $sys, $resindex, $profitindex\n";
	if ($sys2value{$sys} > 0) {
	    $Sys2Expr{$sys} .= " + settings[$resindex] * $sys2value{$sys} + settings[$profitindex] * $sys2profit{$sys}";
	}
    }
}

# Build up the data structures that describe the possible settings.
# This routine takes an id, a label, and a SQL query. The query
# should return a list of systems. Those systems are set to 1.
# Others are set to 0.

sub ScoreSystem {
    my($id, $label, $q, @rest) = @_;
    my($sys);
    push(@Settings, $id);
    foreach $sys (SelectAll($q, @rest)) {
	$Sys2Expr{$sys} .= " + settings[$#Settings]";
    }
    push(@FormElems, "<tr><td>$label</td><td><input name=$id size=4></td></tr>");
}

# Same as above, but for each "area" (Engineering, Science, Medical, Weaponry).
# Takes the same arguments, but $id will be prepended with e,s,m, or w, and
# $label and $q will have %area replaces with Engineering, Science etc, and
# %a replaces with e,s, etc.

sub ScoreSystemAreas {
    my($id, $label, $q, @rest) = @_;
    my($formelem);
    $formelem = "<tr><td>$label</td>";
    $formelem .= ScoreSystemArea('e', "Engineering", $id, $q, @rest);
    $formelem .= ScoreSystemArea('s', "Science", $id, $q, @rest);
    $formelem .= ScoreSystemArea('m', "Medical", $id, $q, @rest);
    $formelem .= ScoreSystemArea('w', "Weaponry", $id, $q, @rest);
    $formelem .= "</tr>";
    push(@FormElems, $formelem);
}

# Does the work. Returns a form sub-element string.
sub ScoreSystemArea {
    my($a, $area, $id, $q, @rest) = @_;
    my($sys);

    $id = "$a$id";
    push(@Settings, $id);
    $q =~ s/\%area/$area/g;
    $q =~ s/\%a/$a/g;

    foreach $sys (SelectAll($q, @rest)) {
	$Sys2Expr{$sys} .= " + settings[$#Settings]";
    }
    return "<td><input name=$id size=4></td>";
}

sub add_header {
    my($str, $terms, $i, $nsystems, $nsettings, $settings);
    $nsystems = $#SystemNames+1;
    $nsettings = $#Settings+1;
    $terms = '';
    $settings = '';
    for ($i = 0; $i < $nsettings; $i++) {
	$settings .= "      settings[$i] = toFloat($Settings[$i].value);\n";
    }
	    
    for ($i = 0; $i < $nsystems; $i++) {
	$terms .= "     score[$i] = $Sys2Expr{$SystemNames[$i]};\n";
    }
    $str =<<"EndOfScript";
Pragma: no-cache
Expires: -1
Content-type: text/html

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<META http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<META name="ROBOTS" content="NOINDEX,NOFOLLOW">
<base href="http://janin.org/dow/">
<title>DOW Javascript Custom Page</title>

<script type="text/javascript" language="javascript">

document.captureEvents(Event.KEYPRESS);
document.onkeypress = function (evt) {
    var key = 
      document.all ? event.keyCode :
      evt.which ? evt.which : evt.keyCode;
    if (key == 13) 
      updateSizes();
}

function setSystemSize(system, size) {
     document.getElementById(\"s\"+system).width=size;
     document.getElementById(\"s\"+system).height=size;
}

function toFloat(n) {
   n = parseFloat(n);
   if (isNaN(n)) {
      return 0;
   } else {
      return n;
   }
}

function updateSizes() {
    var score, settings, i;
    var minscore, maxscore;

    score = new Array($nsystems);
    settings = new Array($nsettings);

    with (document.settingsform) {
$settings    }

$terms

    minscore = score[0];
    maxscore = score[0];
    for (i = 1; i < $nsystems; i++) {
        if (score[i] < minscore) {
	    minscore = score[i];
	}
	if (score[i] > maxscore) {
	    maxscore = score[i];
	}
    }
    for (i = 0; i < $nsystems; i++) {
	setSystemSize(i, 20*(score[i]-minscore)/(maxscore-minscore)+1);
    }
}

EndOfScript
    add($str);
    add("\n</script>\n\n");

    $str =<<"EndOfCSS";
<style type="text/css">
<!--
#divsettings {
  position: fixed;
  top: 0;
  bottom: 0;
  right: 0;
  overflow: auto;
}
#divmap {
 position: fixed;
 top: 0;
 bottom: 0;
 left: 0;
 overflow: auto;
}
-->
</style>
EndOfCSS
    add($str);
    add("</head>\n<body>");
}

sub error {
    print STDERR "\nError: ", join("\n", @_), "\n";
    exit;
}


# Update the count of resources passed in the hashref res by
# downloading orders from the server and accounting for buy/sell
# orders. This can be slow.

sub ProcessOrders {
    my($res) = @_;
    my($orders, $line, $ordersurl, $turnfile, $inc, $fh, $n);
    my($option, $resource);
    $ordersurl = SelectOne("select secreturl from donors where donorid=?;", 
			   $Donor->{donorid});
    $ordersurl =~ s/\.htm$/.ord/;
    $orders = get($ordersurl);
    if (!defined($orders) || $orders =~ /^\s*$/) {
	return;	# No orders submitted. Just return.
    }
    $fh = new FileHandle("/Path/to/turns/$Turn/$Donor->{donorid}.html")
	or herror("Unable to access your turn. This should never happen.");
    $inc = 0;	# In <SELECT NAME="c"> tag
    while ($line = <$fh>) {
	if ($line =~ m|<SELECT NAME=\"c\"|) {
	    $inc = 1;
	} elsif ($inc) {
	    if ($line =~ m|</SELECT>|) {
		$inc=0;
		last;
	    } elsif ($line =~ m|<OPTION VALUE=(.*)>Sell ([0-9]+) (.*) to .* Colony for| ||
		     $line =~ m|<OPTION VALUE=(.*)>Buy ([0-9]+) (.*) for|) {
		$option = $1;
		$n = $2;
		$resource = $3;
		if ($line =~ m|<OPTION VALUE=$option>Sell|) {
		    $n = -$n;
		} elsif ($line !~ m|<OPTION VALUE=$option>Buy|) {
		    herror("No matching buy/sell order. This should never happen.");
		}
		if ($orders =~ /^c=$option$/m) {
		    #print STDERR "Transferring $n $resource\n";
		    $res->{$resource} += $n;
		}
	    }
	}
    }
    foreach $resource (keys(%$res)) {
	if ($res->{$resource} <= 0) {
	    delete($res->{$resource});
	}
    }
	
    $fh->close();
}
