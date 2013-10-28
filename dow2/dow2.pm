#!/usr/bin/perl -w

use strict;
use POSIX;
use FileHandle;

use jcgi;       # Make sure caller has access to these
use jdb;

package dow2;
require Exporter;

use jcgi;	# Make sure we have access to these. Is this the right way to do this?
use jdb;

use vars qw (@ISA @EXPORT_OK @EXPORT);

@ISA = qw ( Exporter );

@EXPORT = qw ( GetCryptedPassword CheckPassword GetDowDataCL GetDowDataPW 
	       AddDowHeader AddDowFooter
	       NameToFilename FilenameToName RaceOfShip
	       ShipIsAlien TechNameToLevel TechLevelToName TechRE 
	       ItemNameToType ItemTypeToName OpenLogs CloseLogs message error warning );

@EXPORT_OK = qw ( );

use vars qw($MessageFH $WarningFH $ErrorFH @ValidSalt);

######################################################################
#
# The crypt stuff is only used in forms to hand around the DOW
# password in encrypted form.
#

@ValidSalt = qw(a b c d e f g h i j k l m n o p q r s t u v w x y z
		A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
		0 1 2 3 4 5 6 7 8 9 );

######################################################################
#
# Return a crypted version of the user's password. Note that this
# is pretty weak encryption.
#

sub GetCryptedPassword {
    my($name) = @_;
    
    return crypt(SelectOne("select password from donordata where ship=?;", $name),
		 $ValidSalt[rand($#ValidSalt)] . $ValidSalt[rand($#ValidSalt)]);
}

######################################################################
#
# Given a username and ENCRYPTED password,
# check if the password matches the database.
#
# NOTE: Only the first 8 characters are actually used in crypt.
# Perhaps I should switch to MD5.
#

sub CheckPassword {
    my($ship, $cryptpw) = @_;
    my($pw);
    $pw = SelectOne("select password from donordata where ship=?;", $ship);
    return crypt($pw, substr($cryptpw, 0, 2)) eq $cryptpw;
} # CheckPassword()


######################################################################
#
# Get DOW data structure from command line arguments.
#

sub GetDowDataCL {
    my($remote_user, $ship);

    OpenDB("dow2");
    
    # Check if access appears to be via web or via command line
    # Is there a better way to do this?
    
    if (!exists($ENV{REMOTE_USER})) {
	# Not web access.
	$remote_user = 'admin';
    } else {
	$remote_user = $ENV{REMOTE_USER};
    }

    $remote_user =~ s/\\//g;
    $ship = $remote_user;

    if (ExistsSelect("select * from permissions where ship=? and name='browse_as' and value='true';", $remote_user)) {
	$ship = SelectOneWithDefault("select value from hiddendata where ship=? and name='browsing_as';", $remote_user, $remote_user);
    }

    return { ship => $ship,
	     turn => SelectOne("select max(turn) from downloadfiles where type='Player' and status='Done' and name=?;", $ship)
	     }
};

# Given a DOW ship and crypted password, return the dow data structure.
# Verify that it matches.

sub GetDowDataPW {
    my($ship, $dowpw) = @_;
    OpenDB("dow2");
    if (!CheckPassword($ship, $dowpw)) {
	herror("Password mismatch. This shouldn't happen.");
    }
    return { ship => $ship,
	     turn => SelectOne("select max(turn) from downloadfiles where type='Player' and status='Done' and name=?;", $ship)
	     }
};


# Add HTML header and footer. Will eventually select css, etc.

sub AddDowHeader {
    my($data, $args) = @_;
    my($str);
    if (ref($args) ne 'HASH') {
	$args = { };
    }
    if (!exists($args->{title})) {
	$args->{title} = '';
    }
    if (!exists($args->{base})) {
	$args->{base} = SelectOne("select weburl from params;");
    }
    if (!exists($args->{head})) {
	$args->{head} = '';
    }
    if (!exists($args->{sidebar})) {
	$args->{sidebar} = 0;
    }
    $str =<<"EndOfHeader";
Pragma: no-cache
Expires: -1
Content-type: text/html

<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">
<html>
<head>
<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\" />
<meta name=\"ROBOTS\" content=\"NOINDEX,NOFOLLOW\" />
<base href=\"$args->{base}/\" />
<title>$args->{title}</title>
$args->{head}
</head>
<body>
EndOfHeader
    add($str);
}

sub AddDowFooter {
    my($data) = @_;
    add("\n\n</body>\n</html>\n");
}

# Given a tech name, return the level (e.g. primitive = 1)

sub TechNameToLevel {
    my($tn) = @_;
    my %tns = qw(primitive 1 basic 2 mediocre 3 advanced 4 exotic 5 magic 6);
    if (! exists($tns{lc($tn)})) {
	my_error("Unable to find tech level of tech name $tn");
    }
    return $tns{lc($tn)};
}

sub TechLevelToName {
    my($tl) = @_;
    my @tls = qw( Primitive Basic Mediocre Advanced Exotic Magic );
    if ($tl !~ /^\s*[123456]\s*$/) {
	my_error("Illegal tech level $tl");
    }
    return $tls[$tl-1];
}

sub TechRE {
    return "(?:primitive)|(?:basic)|(?:mediocre)|(?:advanced)|(?:exotic)|(?:magic)";
}


# Given a module/pod/artifact name, return the type number.

sub ItemTypeToName {
    my($i) = @_;
    my @n = ('Warp Drive', 'Impulse Drive', 'Sensor', 'Cloak', 'Life Support', 'Sickbay', 'Shield', 'Ram', 'Gun', 'Disruptor', 'Laser', 'Missile', 'Drone', 'Fighter', 'Pod');
    return $n[$i-1];
}

sub ItemNameToType {
    my($item) = @_;
    if ($item =~ /^warp/i) {
	return 1;
    } elsif ($item =~ /^impulse/i) {
	return 2;
    } elsif ($item =~ /^sensor/i) {
	return 3;
    } elsif ($item =~ /^cloak/i) {
	return 4;
    } elsif ($item =~ /^life/i) {
	return 5;
    } elsif ($item =~ /^sickbay/i) {
	return 6;
    } elsif ($item =~ /^shield/i) {
	return 7;
    } elsif ($item =~ /^ram/i) {
	return 8;
    } elsif ($item =~ /^gun/i) {
	return 9;
    } elsif ($item =~ /^disruptor/i) {
	return 10;
    } elsif ($item =~ /^laser/i) {
	return 11;
    } elsif ($item =~ /^missile/i) {
	return 12;
    } elsif ($item =~ /^drone/i) {
	return 13;
    } elsif ($item =~ /^fighter/i) {
	return 14;
    } elsif ($item =~ /^pod/i) {
	return 15;
    } else {
	my_error("Unexpected item $item");
    }
}


sub FilenameToName {
    my($name) = @_;
    $name =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;   # % -> char
    return $name;    
}

sub NameToFilename {
    my($name) = @_;
    $name =~ s/([^a-zA-Z0-9_. -])/sprintf("%%%02x", ord($1))/ge;
    return $name;
}

# Return the race of the alien ship, or undef if its a player
sub RaceOfShip {
    my($ship) = @_;
    if ($ship =~ /^\s*((:?Ant)|(:?Beetle)|(:?Bird)|(:?Cat)|(:?Dog)|(:?Elf)|(:?Fish)|(:?Goblin)|(:?Groundhog)|(:?Hamster)|(:?Kangaroo)|(:?Lizard)|(:?Lobster)|(:?Monkey)|(:?Otter)|(:?Penguin)|(:?Pig)|(:?Pixie)|(:?Rabbit)|(:?Rat)|(:?Sloth)|(:?Snake)|(:?Spider)|(:?Squirrel)|(:?Tiger)|(:?Troll)|(:?Turtle)|(:?Vole)|(:?Wasp)|(:?Weasel)|(:?Worm)|(:?Zebra))\s*[0-9]+\s*$/) {
	return $1;
    } else {
	return undef;
    }
}

# Return true if the ship is an alien, false otherwise

sub ShipIsAlien {
    my($ship) = @_;
    return defined(RaceOfShip($ship));
}

######################################################################
#
# Try to handle errors gracefully.
#
# If called by routines that use the logging service, use error().
# If called by a cgi script, use herror.
# Otherwise, print message and die.
#
# Total hack:
#
# If $ErrorFH is defined, use error() for logging service
# Otherwise, if $ENV{SERVER_NAME} is defined, use herror.
# Otherwise, just print to stderr and exit.

sub my_error {
    if (defined($ErrorFH)) {
	error(@_);
    } elsif (exists($ENV{SERVER_NAME})) {
	herror(@_);
    } else {
	print STDERR "\nError: ", join(" ", @_), "\n\n";
	exit;
    }
}
	

# Log handling

sub OpenLogs {
    my($base, $turn) = @_;
    my($path);
    $path = SelectOne("select topdir from params;") . "/" . SelectOne("select logdir from params;") . "/$turn";
    if (! -d $path) {
	mkdir($path) or die "Couldn't create log directory '$path': $!";
    }
    $MessageFH = new FileHandle(">>$path/$base.messages") or die "Couldn't open messages file $path/$base.messages: $!";
    $WarningFH = new FileHandle(">>$path/$base.warnings") or die "Couldn't open messages file $path/$base.warning: $!";
    $ErrorFH = new FileHandle(">>$path/$base.errors") or die "Couldn't open messages file $path/$base.errors: $!";
}

sub CloseLogs {
    $MessageFH->close();
    $WarningFH->close();
    $ErrorFH->close();
    $ErrorFH = undef;
    $WarningFH = undef;
    $MessageFH = undef;
}
    

sub message {
    my $str = join(' ', @_);
    print $MessageFH "$str\n";
    $MessageFH->flush();
}

sub warning {
    my $str = join(' ', @_);
    print $MessageFH "$str\n";
    print $WarningFH "$str\n";
    print STDERR "Warning: $str\n";
    $MessageFH->flush();
    $WarningFH->flush();
}

sub error {
    my $str = join(' ', @_);
    print $MessageFH "ERROR: $str\n";
    print $WarningFH "ERROR: $str\n";
    print STDERR "ERROR: $str\n";
    $MessageFH->flush();
    $WarningFH->flush();
    exit;
}

1;
