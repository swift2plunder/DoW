#!/usr/bin/perl -w
#
# Experimental web page to change sharing settings.
#

use strict;

use dow2;

my($Data, $NShips, $NPanes);

$Data = GetDowDataCL();

MakePage();
PrintPageData();

CloseDB();

exit;

sub MakePage {
    my($p, $sth, $row, $checked);
    $NShips = SelectOne("select count(*) from activeships where turn=?;", $Data->{turn});
    $NPanes = SelectOne("select count(*) from sharingtypes;") + 1; # +1 for default
    AddDowHeader($Data, 
		 { 
		     title => "Sharing Settings for $Data->{ship}",
		     head => gethead()
		     });
#    add("<form name=\"shareform\" method=\"post\" action=\"testsubmit.cgi\">\n");
    add("<form name=\"shareform\" method=\"post\" action=\"sharing_submit.cgi\">\n");
    add("<input type=\"hidden\" name=\"ship\" value=\"$Data->{ship}\" />\n");
    add("<input type=\"hidden\" name=\"password\" value=\"" . GetCryptedPassword($Data->{ship}) . "\" />\n");
    add("<input type=\"hidden\" name=\"turn\" value=\"$Data->{turn}\" />\n");
    add("<div id=\"sharediv\">\n");
    add("<input type=\"radio\" name=\"shareradio\" value=\"default\" onclick=\"setPane(1);\" checked=\"checked\" /> Default\n\n");
    $sth = mydo('select * from sharingtypes order by name;');
    $p = 2;
    while ($row = $sth->fetchrow_hashref()) {
	add("<br />\n");
	add("<input type=\"radio\" name=\"shareradio\" value=\"$row->{shortname}\" onclick=\"setPane($p);\" /> $row->{name}\n");
	$p++;
    }
    $sth->finish();
    add("</div>\n\n");
    add("<div id=\"submitdiv\"><input type=\"submit\" /> &nbsp; <input type=\"reset\" value=\"Reset All\" /></div>\n");
    add("<div id=\"shiplistdiv\">\n");

    add("<div id=\"pane1\">\n");
    add("<p>Default (used for all other settings that have \"Use Default Settings\" selected).</p>\n<br /> <br />\n");
    add("<input type=\"button\" onclick=\"selectAllShips('pane1');\" value=\"Select All\" /> &nbsp; <input type=\"button\" onclick=\"selectNoShips('pane1');\" value=\"Select None\" />\n");
    addshipsection(1, 'default');
    $sth = mydo('select * from sharingtypes order by name;');
    $p = 2;
    while ($row = $sth->fetchrow_hashref()) {
	add("<div id=\"pane$p\">\n");
	add("<p>$row->{description}</p>\n\n");
	if (SelectOneWithDefault("select usedefault from lsharingsettings where ship=? and sharetypeid=?;", 1,
		      $Data->{ship}, $row->{sharetypeid})) {
	    $checked = "checked=\"checked\"";
	} else {
	    $checked = '';
	}
	
	add("<input $checked type=\"checkbox\" name=\"$row->{shortname}_default\" onclick=\"setDefault('pane$p', this.checked);\" />Use Default Settings<br /> <br />\n\n");
	add("<input type=\"button\" onclick=\"selectAllShips('pane$p');\" value=\"Select All\" /> &nbsp; <input type=\"button\" onclick=\"selectNoShips('pane$p');\" value=\"Select None\" /><br />\n");
	addshipsection($p, $row->{shortname});
	$p++;
    }
    $sth->finish();
    add("</div>\n");
    
    add("</form>\n");
    AddDowFooter($Data);
}

sub addshipsection {
    my($p, $shortname) = @_;
    my($sth, $row, $n, $checked, $typeid);
    if ($shortname ne 'default') {	
	$typeid = SelectOne("select sharetypeid from sharingtypes where shortname=?;", $shortname);
    }
    add("<table>\n");
    $sth = mydo("select * from activeships where turn=? order by ship;", $Data->{turn});
    $n = 0;
    while ($row = $sth->fetchrow_hashref()) {
	if ($n % 6 == 0) {
	    add("<tr>");
	}
	if (($shortname eq 'default' && ExistsSelect("select * from lsharingsettings set, sharingships ships where set.id=ships.id and sharetypeid is NULL and set.ship=? and ships.ship=?;", $Data->{ship}, $row->{ship})) ||
	    ($shortname ne 'default' && ExistsSelect("select * from lsharingsettings set, sharingships ships where set.id=ships.id and sharetypeid=$typeid and set.ship=? and ships.ship=?;", $Data->{ship}, $row->{ship}))) {
	    $checked = "checked=\"checked\"";
	} else {
	    $checked = '';
	}
	add("<td><input $checked type=\"checkbox\" name=\"$shortname" . "_$row->{id}\" id=\"pane$p" . "_" . ($n+1) . "\" />$row->{ship}</td>\n");
	if ($n % 6 == 5) {
	    add("</tr>\n");
	}
	$n++;
    }
    if ($n % 6 != 5) {
	add("</tr>\n");
    }
    $sth->finish();
    add("</table><br /> <br />\n");
    add("<input type=\"button\" onclick=\"selectAllShips('pane$p');\" value=\"Select All\" /> &nbsp; <input type=\"button\" onclick=\"selectNoShips('pane$p');\" value=\"Select None\" />\n");
    add("</div>\n");
}


sub gethead {
    my($ret, $ii);
    $ret = "<style type=\"text/css\">\n#pane1 { display: block; }\n";
    for ($ii = 2; $ii <= $NPanes; $ii++) {
	$ret .= "#pane$ii { display: none; }\n";
    }
    $ret .=<<"EndOfHead";
#sharediv {
  position : fixed;
  width : 50%;
  height : 155px;
  top : 0;
  right : 0;
  bottom : auto;
  left : 0;
  border-bottom : 2px solid #00cccc;
}

#submitdiv {
  position : fixed;
  width : 50%;
  height : 155px;
  top : 0;
  right : 0;
  bottom : auto;
  left : auto;
  border-bottom : 2px solid #00cccc;
}


#shiplistdiv {
  position: fixed;
  height: auto;
  left: 0px;
  right: 0px;
  top: 155px;
  bottom: 0px;
  margin: 0px 0px 0px 0px;
  padding-left: 0px;
  padding-right: 0px;
  padding-top: 0px;
  color: #000000;
  overflow: auto;
  font-size: smaller;
}

</style>

<script type="text/javascript">
<!--

var nships = $NShips;
var npanes = $NPanes;

function setPane(n) {
   var p, ii;
   
   for (ii = 1; ii <= npanes; ii++) {
       p = document.getElementById(\"pane\" + ii);
       p.style.display=\"none\";
   }
   p = document.getElementById(\"pane\" + n);
   p.style.display=\"block\";
}

function selectAllShips(id) {
  var ii;
  for (ii = 1; ii <= nships; ii++) {
     document.getElementById(id + \"_\" + ii).checked = true;
  }
}

function selectNoShips(id) {
  var ii;
  var b;
  for (ii = 1; ii <= nships; ii++) {
     document.getElementById(id + \"_\" + ii).checked = false;
  }
}

function setDefault(id, state) {
  var b;
  for (var ii=1; ii <= nships; ii++) {
     b = document.getElementById(id + \"_\" + ii);
     if (state == true) {
        b.checked = document.getElementById(\"pane1_\" + ii).checked;
     }
     b.disabled = state;
  }
}
-->
</script>
   
EndOfHead
}
