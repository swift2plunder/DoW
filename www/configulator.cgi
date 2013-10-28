#!/usr/bin/perl -w
#
# Ship configuration calculator
#

use strict;

use dow;

my($Donor, %Form);

if (exists($ENV{REMOTE_USER})) {
    $Donor = ProcessDowCommandline();
} elsif (exists($ENV{CONTENT_LENGTH})) {
    ReadFormData();
} else {
    herror("Couldn't get remote_user or form data!");
}

if ($#ARGV != -1) {
    usage();
}

GeneratePage();
PrintPageData();

CloseDB();

exit;

sub usage {
    herror("Usage: configulator.cgi");
}

sub GeneratePage {
    my($sth, $row, $turn, $curse, @curses, $m, $totalmass, @techtotal, $type);
    my($shipdata, %blesses, %curses, $str, @rely);

    $turn = SelectOne("select max(turn) from turnupdate where donorid=?;", 
		      $Donor->{donorid});
    $shipdata = SelectOneRowAsHash("select * from shipdata where turn=? and donorid=?;",
				   $turn, $Donor->{donorid});
    $sth = mydo("select * from modules where donorid=? and turn=? order by type, tech, reliability;",
		 $Donor->{donorid}, $turn);

    add("<p><hr><p><form method=post action=\"configulator.cgi\">\n");    
    add("<input name=\"dow_pw\" type=hidden value=\"$Donor->{dow_pw}\">\n");
    add("<table>\n");
    add("<tr>");
    add("<th>&nbsp;&nbsp;</th>");
    add("<th align=left>Item</th>");
    add("<th align=left>Tech</th>");
    add("<th>Yield</th>");
    add("<th align=left>Reliability</th>");
    add("</tr>\n");

    $totalmass = 0;
    @techtotal = (0, 0, 0, 0, 0, 0, 0, 0);
    @rely = (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0);

    while ($row = $sth->fetchrow_hashref()) {
	$type = $row->{type}-1;
	if ($type > 7) {
	    $type = 7;
	}
	add("<tr>");
	add("<td><select name=\"$row->{moduleid}\">\n");
	if (exists($Form{$row->{moduleid}})) {
	    $m = $Form{$row->{moduleid}};
	} else {
	    $m = 'none';
	}
	if ($m eq 'none') {
	    add("<option value=none selected>No action</option>\n");
	} else {
	    add("<option value=none>No action</option>\n");
	}
	if ($m eq 'repair') {
	    add("<option value=repair selected>Repair</option>\n");
	    $techtotal[$type] += $row->{tech};
	    $rely[$type] *= $row->{reliability} / 100.0;
	} elsif ($m eq 'break') {
	    add("<option value=break selected>Break</option>\n");
	} else {
	    if ($row->{item} =~ /\(U\)$/) {
		add("<option value=repair>Repair</option>\n");
	    } else {
		add("<option value=break>Break</option>\n");
		if ($m ne 'drop') {
		    $techtotal[$type] += $row->{tech};
		    $rely[$type] *= $row->{reliability} / 100.0;
		}
	    }
	}
	if ($m eq 'drop') {
	    add("<option value=drop selected>Drop</option>\n");
	} else {
	    $totalmass++;
	    add("<option value=drop>Drop</option>\n");
	}
	add("</select></td>\n");
	add("<td>$row->{item} &nbsp; </td>");
	add("<td>" . TechLevelToName($row->{tech}) . " &nbsp; </td>");
	add("<td align=center>$row->{yield}</td>");
	add("<td align=left>$row->{reliability}%</td>");
	add("</tr>\n");
    }
    $sth->finish();
    add("</table>\n");

    #  Pods
    $sth = mydo("select * from pods where donorid=? and turn=?;",
		$Donor->{donorid}, $turn);
    add("<table>\n");
    add("<tr><th>&nbsp;</th>\n");
    add("<th align=left>Item</th>\n");
    add("<th align=left>Resource</th>\n");
    add("<th align=left>Carry</th>\n");
    add("</tr>\n");
    while ($row = $sth->fetchrow_hashref()) {
	add("<tr>\n");
	add("<td><select name=\"$row->{name}\">\n");
	if (exists($Form{$row->{name}})) {
	    $m = $Form{$row->{name}};
	} else {
	    $m = 'none';
	}
	if ($m eq 'none') {
	    add("<option value=none selected>No action</option>\n");
	} else {
	    add("<option value=none>No action</option>\n");
	}
	if ($m eq 'empty') {
	    add("<option value=empty selected>Empty</option>\n");
	    if ($row->{capacity} > $row->{n}) {
		add("<option value=fill>Fill</option>\n");
	    }
	} elsif ($m eq 'fill') {
	    add("<option value=fill selected>Fill</option>\n");
	    if ($row->{n} > 0) {
		add("<option value=empty>Empty</option>\n");
	    }
	    $totalmass += $row->{capacity};
	} else {
	    if ($row->{n} > 0) {
		add("<option value=empty>Empty</option>\n");
	    }
	    if ($row->{capacity} > $row->{n}) {
		add("<option value=fill>Fill</option>\n");
	    }
	    if ($m ne 'drop') {
		$totalmass += $row->{n};
	    }
	}
	if ($m eq 'drop') {
	    add("<option value=drop selected>Drop</option>\n");
	} else {
	    $totalmass++;
	    add("<option value=drop>Drop</option>\n");
	}
	add("</select></td>\n");
	add("<td>$row->{name}&nbsp;&nbsp;&nbsp;</td>\n");
	add("<td>$row->{resource}</td>\n");
	add("<td>$row->{n} / $row->{capacity}</td>\n");
	add("</tr>\n");
    }
    $sth->finish();
    add("</table>\n");    

    # Artifacts
    $sth = mydo("select * from artifacts where donorid=? and turn=?;",
		$Donor->{donorid}, $turn);
    add("<table>\n");
    add("<tr><th>&nbsp;</th>\n");
    add("<th align=left>Name</th>\n");
    add("<th align=left>Bless</th>\n");
    add("<th align=left>Curses</th>\n");
    add("</tr>\n");
    while ($row = $sth->fetchrow_hashref()) {
	@curses = SelectAll("select curse from curses where artifactid=?;",
			    $row->{artifactid});
	add("<tr>\n");
	add("<td><select name=\"$row->{name}\">\n");
	if (exists($Form{$row->{name}})) {
	    $m = $Form{$row->{name}};
	} else {
	    $m = 'none';
	}
	if ($m eq 'none') {
	    add("<option value=none selected>No action&nbsp;&nbsp;&nbsp;</option>\n");
	} else {
	    add("<option value=none>No action&nbsp;&nbsp;&nbsp;</option>\n");
	}
	if ($#curses >= 0) {
	    if ($m eq 'uncurse') {
		add("<option value=uncurse selected>Uncurse All</option>\n");
	    } else {
		add("<option value=uncurse>Uncurse All</option>\n");
	    }
	    foreach $curse (@curses) {
		if ($m eq $curse) {
		    add("<option value=$curse selected>Uncurse $curse</option>\n");
		} else {
		    add("<option value=$curse>Uncurse $curse</option>\n");
		    if ($m ne 'uncurse' && $m ne 'drop') {
			$curses{$curse} = 1;
		    }
		}
	    }
	}
	if ($m eq 'drop') {
	    add("<option value=drop selected>Drop</option>\n");
	} else {
	    add("<option value=drop>Drop</option>\n");
	    $blesses{$row->{bless}} = 1;
	}
	add("</select></td>\n");
	add("<td>$row->{name}&nbsp;&nbsp;&nbsp;</td>\n");
	add("<td>$row->{bless}</td>\n");
	add("<td>");
	if ($#curses >= 0) {
	    add(join(", ", @curses));
	} else {
	    add("&nbsp;");
	}
	add("</td>\n");
	add("</tr>\n");
    }
    $sth->finish();
    add("</table>\n");    

    add("<p><input type=submit> &nbsp; <input type=reset>\n");
    add("</form>\n");
    add(DOW_HTML_Footer($Donor));

    $str = DOW_HTML_Header($Donor, "Configulator");
#    $str .= "\nTotal Mass: $totalmass<p>";
    $str .= "<p><hr><p>Module Factors:<p>\n";
    $str .= "Warp ";
    $str .= ps('Wd', $totalmass, $techtotal[0], $shipdata->{engskill}, \%blesses, \%curses);
    $str .= "%, Impulse ";
    $str .= ps('Id', $totalmass, $techtotal[1], $shipdata->{engskill}, \%blesses, \%curses);

    $str .= "%, Sensor ";
    $str .= ps('Sn', $totalmass, $techtotal[2], $shipdata->{sciskill}, \%blesses, \%curses);
    $str .= "%, Cloak ";
    $str .= ps('Cl', $totalmass, $techtotal[3], $shipdata->{sciskill}, \%blesses, \%curses);

    $str .= "%, Life Support ";
    $str .= ps('Ls', $totalmass, $techtotal[4], $shipdata->{medskill}, \%blesses, \%curses);
    $str .= "%, Sickbay ";
    $str .= ps('Sb', $totalmass, $techtotal[5], $shipdata->{medskill}, \%blesses, \%curses);

    $str .= "%, Shield ";
    $str .= ps('Sh', $totalmass, $techtotal[6], $shipdata->{weapskill}, \%blesses, \%curses);
    $str .= "%, Weapon ";
    $str .= ps('Wp', $totalmass, $techtotal[7], $shipdata->{weapskill}, \%blesses, \%curses);
    $str .= "%";

    $str .= "<p><hr><p>Chance that one or more modules will break per turn:<p>\n";
    $str .= sprintf("Warp: %5.1f%%, ", 100.0 - $rely[0]*100.0);
    $str .= sprintf("Impulse: %5.1f%%, ", 100.0 - $rely[1]*100.0);
    $str .= sprintf("Sensor: %5.1f%%, ", 100.0 - $rely[2]*100.0);
    $str .= sprintf("Cloak: %5.1f%%, ", 100.0 - $rely[3]*100.0);
    $str .= sprintf("Life Support: %5.1f%%, ", 100.0 - $rely[4]*100.0);
    $str .= sprintf("Sickbay: %5.1f%%, ", 100.0 - $rely[5]*100.0);
    $str .= sprintf("Shield: %5.1f%%, ", 100.0 - $rely[6]*100.0);
    $str .= sprintf("Weapon: %5.1f%%\n<p>", 100.0 - $rely[7]*100.0);
    $str .= sprintf("Engineering: %5.1f%%, ", 100.0 - $rely[0]*$rely[1]*100.0);
    $str .= sprintf("Science: %5.1f%%, ", 100.0 - $rely[2]*$rely[3]*100.0);
    $str .= sprintf("Medical: %5.1f%%, ", 100.0 - $rely[4]*$rely[5]*100.0);
    $str .= sprintf("Weaponry: %5.1f%%, ", 100.0 - $rely[6]*$rely[7]*100.0);

    PageDataPrepend($str);    
}

sub ps {
    # $tag - Wd, Id, Sn, Cl, Ls, Sb, Sh, Wp
    # $totalmass - Total mass of the ship
    # $totaltech - Sum of tech levels in the appropriate area (e.g. warp, impulse, etc)
    # $skill - Officer skill in the area (e.g. medical skill)
    # $blesses - $blesses->{$tag} will be set if there's a bless artifact for $tag
    # $curses - $curses->{$tag} will be set if there's a cursed artifact for $tag

    my($tag, $totalmass, $techtotal, $skill, $blesses, $curses) = @_;
    my($val, $tot);
    $val = 100.0 * $techtotal / $totalmass;
    if ($skill > 2*$val) {
	$tot = int($val) + int(2*$val);
    } else {
	$tot = int($skill + $val);
    }
    if (exists($blesses->{$tag})) {
	$tot = int(3*$tot/2);
    }
    if (exists($curses->{$tag})) {
	$tot = int($tot/2);
    }
    #return "$techtotal $skill $tot";
    return $tot;
}

sub ReadFormData {
    my($buffer, @namevals, $nameval, $name, $value);
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
	$Form{$name} = $value;
    }
    if (!exists($Form{dow_pw})) {
	herror("Couldn't get donor from form");
    }
    OpenDB();
    $Donor = SelectOneRowAsHash("select * from donors where dow_pw=?;",
				$Form{dow_pw});
}
