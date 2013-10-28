#!/usr/bin/perl -w
#
# Example call:
#
# http://janin.org/dow/combat_options.cgi?ship1=Auiran&ship2=Spartacus&terrain=Asteroid&homeworld=0

use strict;
use LWP;

use dow;

my($Donor);

$Donor = ProcessDowCommandline();

my %artifact_lookup;	# {$numeric_id} = $name

my %alien_letter = (
		    'Ant'		=> 'A',
		    'Beetle'	=> 'B',
		    'Bird'		=> 'C',
		    'Cat'		=> 'D',
		    'Dog'		=> 'E',
		    'Elf'		=> 'F',
		    'Fish'		=> 'G',
		    'Groundhog'	=> 'H',
		    'Kangaroo'	=> 'I',
		    'Lizard'	=> 'J',
		    'Lobster'	=> 'K',
		    'Monkey'	=> 'L',
		    'Otter'		=> 'M',
		    'Penguin'	=> 'N',
		    'Pig'		=> 'O',
		    'Pixie'		=> 'P',
		    'Rabbit'	=> 'Q',
		    'Sloth'		=> 'R',
		    'Spider'	=> 'S',
		    'Tiger'		=> 'T',
		    'Troll'		=> 'U',
		    'Turtle'	=> 'V',
		    'Vole'		=> 'W',
		    'Wasp'		=> 'X',
		    'Zebra'		=> 'Y',
		    'Hamster'	=> 'Z',
		    'Squirrel'	=> '[',
		    'Worm'		=> '\\',
		    'Goblin'	=> ']',
		    'Rat'		=> '^',
		    'Snake'		=> '_',
		    'Weasel'	=> '`',
		    );

my %colors = (
	      'red'	=> 'ff0000',
	      );

my %blessing_type = (
		     'Wd' => 'warp drive',
		     'Id' => 'impulse drive',
		     'Sn' => 'sensor',
		     'Cl' => 'cloak',
		     'Ls' => 'life support',
		     'Sb' => 'sickbay',
		     'Sh' => 'shield',
		     'Wp' => 'weapon',
		     );

my %skill_types = (
		   'Engineering' => [ 'warp drive', 'impulse drive' ],
		   'Science' => [ 'sensor', 'cloak' ],
		   'Medical' => [ 'life support', 'sickbay' ],
		   'Weaponry' => [ 'shield', 'weapon' ],
		   );

my %weapons = (
	       'ram'		=> 0,
	       'gun'		=> 1,
	       'disruptor'	=> 2,
	       'laser'		=> 3,
	       'missile'	=> 4,
	       'drone'		=> 5,
	       'fighter'	=> 6,
	       );

my %tech_levels = (
		   'Primitive'	=> 1,
		   'Basic'		=> 2,
		   'Mediocre'	=> 3,
		   'Advanced'	=> 4,
		   'Exotic'	=> 5,
		   'Magic'		=> 6,
		   );

my @tech_levels = (undef, 'Primitive', 'Basic', 'Mediocre', 'Advanced', 'Exotic', 'Magic');

my %blessing_order = (
		      'Wd' => -1,
		      'Id' => 0,
		      'Sn' => 1,
		      'Cl' => 2,
		      'Ls' => -1,
		      'Sb' => -1,
		      'Sh' => 3,
		      'Wp' => 4,
		      );

my @ranges = (
	      'Adjacent',
	      'Close',
	      'Short',
	      'Medium',
	      'Long',
	      'Distant',
	      'Remote',
	      );

my %ranges = (
	      'Adjacent'	=> 0,
	      'Close'		=> 1,
	      'Short'		=> 2,
	      'Medium'	=> 3,
	      'Long'		=> 4,
	      'Distant'	=> 5,
	      'Remote'	=> 6,
	      );

my %module_types = (
		    'warp drive'	=> 0,
		    'impulse drive'	=> 1,
		    'sensor'	=> 2,
		    'cloak'		=> 3,
		    'life support'	=> 4,
		    'sickbay'	=> 5,
		    'shield'	=> 6,
		    'ram'		=> 7,
		    'gun'		=> 8,
		    'disruptor'	=> 9,
		    'laser'		=> 10,
		    'missile'	=> 11,
		    'drone'		=> 12,
		    'fighter'	=> 13,
		    'pod'		=> 14,
		    );

sub strip_spaces {
    $_[0] =~ s/\n<\/a><\/i><\/em><\/strong><HR>.*\n/\n/ig;
    $_[0] =~ s/\s+/ /g;
    $_[0] =~ s/> />/g;
    $_[0] =~ s/ </</g;
    $_[0] =~ s/^ //;
    $_[0] =~ s/ $//;
}

sub min {
    if (@_ > 0) {
	my $i = $_[0];
	my $j;
	foreach $j (@_) {
	    if ($i > $j) {
		$i = $j;
	    }
	}
	$i;
    } else {
	undef;
    }
}

sub max {
    if (@_ > 0) {
	my $i = $_[0];
	my $j;
	foreach $j (@_) {
	    if ($i < $j) {
		$i = $j;
	    }
	}
	$i;
    } else {
	undef;
    }
}

sub extract_fields {
    my ($i) = @_;
    my %field;
    while ($i =~ /(?:^|&)([^=&]+)=([^&]*)/g) {
	my ($name, $value) = ($1, $2);
	$name =~ s/%(..)/pack('c', hex($1))/ge;
	$value =~ s/\+/ /g;
	$value =~ s/%(..)/pack('c', hex($1))/ge;
	if (defined($field{$name})) {
	    $field{$name} .= "+$value";
	} else {
	    $field{$name} = $value;
	}
    }
    \%field;
}

sub calc_skill {
    my ($old_factors, $factors, $blessings, $curses, $skill) = @_;
    my @i;
    my @maxed;
    my $j = 0;
    my $factor;
    foreach $factor (@{$skill_types{$skill}}) {
	if ($old_factors->{$factor} > int($factors->{$factor}) + int(2 * $factors->{$factor}) || $old_factors->{$factor} > int($factors->{$factor}) + 64) {
	    if (defined($curses->{$factor}) && $old_factors->{$factor} - 1 <= int($factors->{$factor}) + int(2 * $factors->{$factor}) && $old_factors->{$factor} - 1 <= int($factors->{$factor}) + 64) {
		$old_factors->{$factor}--;
	    } elsif (!defined($blessings->{$factor})) {
		$blessings->{$factor} = 1;
		$old_factors->{$factor} = int($old_factors->{$factor} / 1.5 + 0.5);
	    }
	}
	$i[$j] = $old_factors->{$factor} - int($factors->{$factor});
	$maxed[$j] = $i[$j] >= int(2 * $factors->{$factor});
	$j++;
    }
    (\@i, \@maxed);
}

sub find_player_skills {
    my ($file) = @_;
    my $mass = 0;
    my %blessings;
    my %curses;
    my %factors;
    my %skills;
    $file =~ /Warp (\d+)%, Impulse (\d+)%, Sensor (\d+)%, Cloak (\d+)%, Life Support (\d+)%, Sickbay (\d+)%, Shield (\d+)%, Weapon (\d+)%/i;
    my %old_factors = (
		       'warp drive' => $1,
		       'impulse drive' => $2,
		       'sensor' => $3,
		       'cloak' => $4,
		       'life support' => $5,
		       'sickbay' => $6,
		       'shield' => $7,
		       'weapon' => $8,
		       );
    while ($file =~ /<TR[^>]*><TD>(?:<a href=\"\.\.\/modules\/[^.]*\.html\">)?([^-<\(]+)(?:-\d+D?)?(?:<\/a>)?( ?\(U\))?<\/TD><TD>([^<]+)<\/TD><TD>([^<]+)<\/TD><TD>(\d+)<\/TD>(?:<\/TR>)?/ig) {
	# $module_type, $broken, $tech | $capacity | $blessing | $bio_bombs, $reliability | $cargo | $curses | $logic_bombs, $ey | $load | $keys | $bangy_bombs
	my ($module_type, $broken, $tech, $curses, $load) = ($1, $2, $3, $4, $5);
	if ($module_type !~ /^[A-Z]/) {
	    $mass++;
	}
	if (defined($broken)) {
	} elsif ($module_type =~ /^[A-Z]/) {
	    $blessings{$blessing_type{$tech}} = 1;
	    if ($curses ne 'None') {
		my $i;
		for ($i = 0; $i < length($curses); $i += 2) {
		    $curses{$blessing_type{substr($curses, $i, 2)}} = 1;
		}
	    }
	} elsif ($module_type eq 'pod') {
	    $mass += $load;
	} elsif (defined($weapons{$module_type})) {
	    $factors{'weapon'} += $tech_levels{$tech};
	} else {
	    $factors{$module_type} += $tech_levels{$tech};
	}
    }
    my $blessing;
    foreach $blessing (keys(%blessings)) {
	$old_factors{$blessing} = int($old_factors{$blessing} / 1.5 + 0.5);
    }
    my $curse;
    foreach $curse (keys(%curses)) {
	$old_factors{$curse} = 2 * $old_factors{$curse} + 1;
    }
    my $i;
    foreach $i (keys(%blessing_type)) {
	my $factor = $blessing_type{$i};
	if (defined($factors{$factor})) {
	    $factors{$factor} = $factors{$factor} * 100 / $mass;
	} else {
	    $factors{$factor} = 0;
	}
    }
    my $skill;
    foreach $skill (keys(%skill_types)) {
	my ($i, $maxed) = &calc_skill(\%old_factors, \%factors, \%blessings, \%curses, $skill);
	if ($i->[0] + 1 < $i->[1] && !$maxed->[0] && !defined($blessings{$skill_types{$skill}[1]})) {
	    $blessings{$skill_types{$skill}[1]} = 1;
	    $old_factors{$skill_types{$skill}[1]} = int($old_factors{$skill_types{$skill}[1]} / 1.5 + 0.5);
	    ($i, $maxed) = &calc_skill(\%old_factors, \%factors, \%blessings, \%curses, $skill);
	} elsif ($i->[1] + 1 < $i->[0] && !$maxed->[1] && !defined($blessings{$skill_types{$skill}[0]})) {
	    $blessings{$skill_types{$skill}[0]} = 1;
	    $old_factors{$skill_types{$skill}[0]} = int($old_factors{$skill_types{$skill}[0]} / 1.5 + 0.5);
	    ($i, $maxed) = &calc_skill(\%old_factors, \%factors, \%blessings, \%curses, $skill);
	}
	my $j = &max(@{$i});
	#if ($maxed->[0] && $maxed->[1]) {
	#	$skills{$skill} = "$j+";
	#} else {
	$skills{$skill} = $j;
	#}
    }
    %skills;
}

sub get_page {
    my ($page) = @_;
    my $ua = LWP::UserAgent->new;
    my $request = HTTP::Request->new(GET => $page);
    my $response = $ua->request($request);
    $response->is_error() ? undef : $response->content;
}

sub read_ship_file {
    my ($ship, $turn, $ship_dir) = @_;
    $ship =~ s/\+/ /g;
    my $is_alien = $ship =~ /^[A-Z][a-z]+ \d+$/;
    my $path = SelectOne("select path from shipconfig where ship=? and turn=?;",
			 $ship, $turn);
    if (open(IN, "< $path")) {
	my $ship_details = join('', <IN>);
	close(IN);
	&strip_spaces($ship_details);
	($ship, $is_alien, $ship_details);
    } else {
	herror("Failed: open: $path");
	return ();
    }
}

sub read_ship {
    my ($url, $turn, $ship_dir) = @_;
    if (!defined($url)) {
	return;
    }
    $url =~ s/\++$//;
    my $ship;
    my $is_alien;
    my $ship_details;
    if ($url =~ /\//) {	# really is a url
	my $page = &get_page($url);
	&strip_spaces($page);
	if ($page =~ /<A NAME=\"?([^\">]+)\"?><\/A><TABLE BORDER=1>.*?<\/TABLE>.*?<\/STRONG><P>(?:<STRONG>[^<]*<P><\/STRONG>(?:<STRONG>[^<]*<BR><P><\/STRONG>)?)?/i) {
	    $ship = $1;
	    $ship_details = $&;
	    $ship =~ s/_/ /g;
	    $ship =~ s/@/\'/g;
	    $is_alien = $ship =~ /^[A-Z][a-z]+ \d+$/;
	}
    } else {
	($ship, $is_alien, $ship_details) = &read_ship_file($url, $turn, $ship_dir);
	if (!defined($turn) && (!defined($ship_details) || $ship_details eq '') && $url =~ s/[+ ](\d+)$//) {
	    $turn = $1;
	    ($ship, $is_alien, $ship_details) = &read_ship_file($url, $turn, $ship_dir);
	}
	$url = undef;
    }
    if (!defined($ship) || !defined($is_alien) || !defined($ship_details)) {
	return;
    }
    my %factors;
    my @modules;
    my %curses;
    my %blessings;
    my $working_modules = 0;
    my $power_rank = 0;
    my $shields = 0;
    my @firepower = (0, 0, 0, 0, 0, 0, 0);
    while ($ship_details =~ /<TR[^>]*><TD>(?:<a[^>]*>)?(([^-<\(]+[^-<\( ])(?:-\d+D?)?)(?:<\/a>)?( ?\(U\))?<\/TD><TD>([^<]+)<\/TD><TD>([^<%]+)%?<\/TD><TD>(\d+)<\/TD>(?:<\/TR>)?/ig) {
	my ($module, $type, $broken, $tech, $reliability, $ey) = ($1, $2, $3, $4, $5, $6);
	if ($type ne 'pod' && $module !~ /^[A-Z]/) {
	    $tech = $tech_levels{$tech};
	}
	if (!defined($broken) && $module !~ /^[A-Z]/) {
	    $power_rank += $tech;
	}
	if ($module =~ /^[^A-Z].*[^D]$/) {
	    $module .= "  ";
	} else {
	    $module .= " ";
	}
	if (defined($broken)) {
	    $module .= "(U)";
	}
	if ((!defined($broken) && $module !~ /^pod/) || $module =~ /^[A-Z]/) {
	    $working_modules++;
	}
	if ($module =~ /^[A-Z]/) {
	    $module .= " [$tech";
	    if ($reliability ne 'None') {
		$module .= " / $reliability";
	    }
	    $module .= "]";
	} else {
	    $module .= " [$tech_levels[$tech]]";
	}
	push(@modules, $module);
	if ($module =~ /^[A-Z]/) {
	} elsif ($type eq 'pod') {
	    $factors{'mass'} += 1 + $ey;
	} else {
	    $factors{'mass'}++;
	}
	if (defined($broken)) {
	} elsif ($type eq 'impulse drive') {
	    $factors{'Id'} += $tech;
	} elsif ($type eq 'sensor') {
	    $factors{'Sn'} += $tech;
	} elsif ($type eq 'cloak') {
	    $factors{'Cl'} += $tech;
	} elsif ($type eq 'shield') {
	    $shields += $tech;
	} elsif (defined($weapons{$type})) {
	    $firepower[$weapons{$type}] += $tech;
	} elsif ($module =~ /^[A-Z]/) {
	    $blessings{$tech}++;
	    if ($reliability ne 'None') {
		my $i;
		for ($i = 0; $i < length($reliability); $i += 2) {
		    $curses{substr($reliability, $i, 2)}++;
		}
	    }
	}
    }
    my $torpedoes;
    if ($ship_details =~ /Torpedo Stock = (\d+)/) {
	$torpedoes = $1;
    } else {
	$torpedoes = 0;
    }
    my $i;
    for ($i = 0; $i < @firepower; $i++) {
	$firepower[$i] *= 5 * (7 - $i);
    }
    for ($i = @firepower - 2; $i >= 0; $i--) {
	$firepower[$i] += $firepower[$i + 1];
    }
    $shields *= 120;
    my $ideal_range;
    for ($ideal_range = $#firepower; $ideal_range >= 0 && $firepower[$ideal_range] == 0; $ideal_range--) { }
    if ($ideal_range == -1) {
	$ideal_range = $#ranges;
    }
    my %skills;
    if (!$is_alien) {
	%skills = $ship_details =~ /<li>Skill Levels<ul><li>(Engineering) (\d+)\+?<\/li><li>(Science) (\d+)\+?<\/li><li>Medical \d+\+?<\/li><li>Weaponry \d+\+?<\/li><\/ul>/;
	if (keys(%skills) != 2) {
	    %skills = &find_player_skills($ship_details);
	}
    }
    my $factor;
    foreach $factor ('Id', 'Sn', 'Cl') {
	$factors{$factor} = &find_factor(\%factors, \%skills, $factor);
    }
    my %enemies;
    if ($ship_details =~ /<h3><a name=enemies>Enemies<\/a><\/h3><ul>(?:<li><a href=\"\.\.\/aliens\/[^>]+\.html\">[^<]+<\/a><\/li>)+<\/ul>/) {
	my $list = $&;
	while ($list =~ /<li><a[^>]+>([^<]+)<\/a><\/li>/g) {
	    $enemies{$1} = 1;
	}
    } elsif ($Donor->{ship} eq $ship) {
	foreach my $enemy (SelectAll("select who from enemies where donorid=? and turn=?;", $Donor->{donorid}, $turn)) {
	    $enemies{$enemy} = 1;
	}
    }

    {
	'name' => $ship,
	'is_alien' => $is_alien,
	'torpedoes' => $torpedoes,
	'modules' => \@modules,
	'shields' => $shields,
	'firepower' => \@firepower,
	'blessings' => \%blessings,
	'curses' => \%curses,
	'factors' => \%factors,
	'working_modules' => $working_modules,
	'ideal_range' => $ideal_range,
	'skills' => \%skills,
	'enemies' => \%enemies,
	'power_rank' => $power_rank,
	'favor' => {
	    'Engineering' => 200,
	    'Science' => 200,
	    'Medical' => 200,
	    'Weaponry' => 200,
	},
	'Enlightenment' => {
	    'Engineering' => 0,
	    'Science' => 0,
	},
	'url' => $url,
	'turn' => $turn,
    };
}

sub find_factor {
    my ($factors, $skills, $type) = @_;
    if (!defined($factors->{$type}) || $factors->{'mass'} == 0) {
	return 0;
    }
    my $factor = 100 * $factors->{$type} / $factors->{'mass'};
    my $skill;
    if ($type eq 'Id') {
	$skill = defined($skills->{'Engineering'}) ? $skills->{'Engineering'} : 0;
    } elsif ($type eq 'Sn' || $type eq 'Cl') {
	$skill = defined($skills->{'Science'}) ? $skills->{'Science'} : 0;
    }
    if ($skill > int(2 * $factor)) {
	$factor = int($factor) + int(2 * $factor);
    } else {
	$factor = int($factor) + $skill;
    }
}

sub find_lucky_module {
    my ($modules, $type) = @_;
    my $found;
    my $module;
    foreach $module (@{$modules}) {
	if ($module =~ /^$type-\d+D?/) {
	    if (defined($found)) {
		return '';
	    }
	    $found = $module;
	}
    }
    $found;
}

sub print_option_list {
    my ($name, $values, $labels, $fields, $options) = @_;
    my %defaults = &get_defaults($fields->{$name});
    print("<td><select name=\"$name\"$options>\n");
    my $i;
    for ($i = 0; $i < @{$values}; $i++) {
	print("<option value=$values->[$i]");
	if (defined($defaults{$values->[$i]})) {
	    print(" selected");
	}
	print(">$labels->[$i]</option>\n");
    }
    print("</select></td>\n");
}

sub print_engineering_spells {
    my ($suffix, $fields, $ship1) = @_;
    my $favor = $ship1->{'favor'}{'Engineering'};
    my @values = ('.');
    my @labels = ('No Spells');
    if ($favor >= 45) {
	push(@values, 7);
	push(@labels, 'Bless Impulse Drive (45)');
    }
    if (defined($ship1->{'curses'}{'Id'}) && $favor >= 70) {
	push(@values, 15);
	push(@labels, 'Uncurse Impulse Drives (70)');
    }
    if (!$ship1->{'Enlightenment'}{'Engineering'} && $favor >= 100) {
	push(@values, 27);
	push(@labels, 'Enlightenment (100)');
    }
    my $lucky = &find_lucky_module($ship1->{'modules'}, 'warp drive');
    if (defined($lucky) && $lucky ne '' && $favor >= 10) {
	push(@values, 76);
	push(@labels, "Lucky $lucky (10)");
    }
    $lucky = &find_lucky_module($ship1->{'modules'}, 'impulse drive');
    if (defined($lucky) && $lucky ne '' && $favor >= 10) {
	push(@values, 77);
	push(@labels, "Lucky $lucky (10)");
    }
    print_option_list("x$suffix", \@values, \@labels, $fields, '');
}

sub print_science_spells {
    my ($suffix, $fields, $ship1) = @_;
    my $favor = $ship1->{'favor'}{'Science'};
    my @values = ('.');
    my @labels = ('No Spells');
    if ($favor >= 45) {
	push(@values, 8, 9);
	push(@labels, 'Bless Sensors (45)', 'Bless Cloaks (45)');
    }
    if (defined($ship1->{'curses'}{'Sn'}) && $favor >= 70) {
	push(@values, 16);
	push(@labels, 'Uncurse Sensors (70)');
    }
    if (defined($ship1->{'curses'}{'Cl'}) && $favor >= 70) {
	push(@values, 17);
	push(@labels, 'Uncurse Cloaks (70)');
    }
    if (!$ship1->{'Enlightenment'}{'Science'} && $favor >= 100) {
	push(@values, 28);
	push(@labels, 'Enlightenment (100)');
    }
    my $lucky = &find_lucky_module($ship1->{'modules'}, 'sensor');
    if (defined($lucky) && $lucky ne '' && $favor >= 10) {
	push(@values, 78);
	push(@labels, "Lucky $lucky (10)");
    }
    $lucky = &find_lucky_module($ship1->{'modules'}, 'cloak');
    if (defined($lucky) && $lucky ne '' && $favor >= 10) {
	push(@values, 79);
	push(@labels, "Lucky $lucky (10)");
    }
    print_option_list("x$suffix", \@values, \@labels, $fields, '');
}

sub print_medical_spells {
    my ($suffix, $fields, $ship1, $ship2, $lucky, $lucky2) = @_;
    my $favor = $ship1->{'favor'}{'Medical'};
    my @values = ('.');
    my @labels = ('No Spells');
    if ($favor >= 75 && $ship2->{'name'} =~ /^([A-Z][a-z]+) \d+$/) {
	push(@values, "5$alien_letter{$1}");
	push(@labels, "Pacify $1 Nation (75)");
    }
    if (defined($lucky) && $lucky ne '' && $favor >= 10) {
	push(@values, 80);
	push(@labels, "Lucky $lucky (10)");
    }
    if (defined($lucky2) && $lucky2 ne '' && $favor >= 10) {
	push(@values, 81);
	push(@labels, "Lucky $lucky2 (10)");
    }
    print_option_list("x$suffix", \@values, \@labels, $fields, '');
}

sub print_weaponry_spells {
    my ($suffix, $fields, $ship1) = @_;
    my $favor = $ship1->{'favor'}{'Weaponry'};
    my @values = ('.');
    my @labels = ('No Spells');
    if ($favor >= 45) {
	push(@values, 12, 13);
	push(@labels, 'Bless Shields (45)', 'Bless Weapons (45)');
    }
    if (defined($ship1->{'curses'}{'Sh'}) && $favor >= 70) {
	push(@values, 20);
	push(@labels, 'Uncurse Shields (70)');
    }
    if (defined($ship1->{'curses'}{'Wp'}) && $favor >= 70) {
	push(@values, 21);
	push(@labels, 'Uncurse Weapons (70)');
    }
    my $lucky = &find_lucky_module($ship1->{'modules'}, 'shield');
    if (defined($lucky) && $lucky ne '' && $favor >= 10) {
	push(@values, 82);
	push(@labels, "Lucky $lucky (10)");
    }
    $lucky = undef;
    my $type;
    foreach $type ('ram', 'gun', 'disruptor', 'laser', 'missile', 'drone', 'fighter') {
	my $lucky2 = &find_lucky_module($ship1->{'modules'}, $type);
	if (!defined($lucky2)) {
	} elsif ($lucky2 eq '' || defined($lucky)) {
	    $lucky = undef;
	    last;
	} else {
	    $lucky = $lucky2;
	}
    }
    if (defined($lucky) && $favor >= 10) {
	push(@values, 83);
	push(@labels, "Lucky $lucky (10)");
    }
    print_option_list("x$suffix", \@values, \@labels, $fields, '');
}

sub print_spells {
    my ($suffix, $fields, $ship1, $ship2) = @_;
    print("<tr align=center><th>Engineering</th>");
    &print_engineering_spells($suffix, $fields, $ship1);
    print("</tr>\n");
    print("<tr align=center><th>Science</th>");
    &print_science_spells($suffix, $fields, $ship1);
    print("</tr>\n");
    my $lucky = &find_lucky_module($ship1->{'modules'}, 'life support');
    my $lucky2 = &find_lucky_module($ship1->{'modules'}, 'sickbay');
    if ($ship2->{'is_alien'} || (defined($lucky) && $lucky ne '') || (defined($lucky2) && $lucky2 ne '')) {
	print("<tr align=center><th>Medical</th>");
	&print_medical_spells($suffix, $fields, $ship1, $ship2, $lucky, $lucky2);
	print("</tr>\n");
    }
    print("<tr align=center><th>Weaponry</th>");
    &print_weaponry_spells($suffix, $fields, $ship1);
    print("</tr>\n");
}

sub get_defaults {
    my ($list) = @_;
    my %defaults;
    if (defined($list)) {
	while ($list =~ /([^+]+)(?:$|\+)/g) {
	    $defaults{$1} = 1;
	}
    }
    %defaults;
}

sub print_diplomatic_option {
    my ($suffix, $fields, $ship1) = @_;
    my @values;
    my @labels;
    if ($ship1->{'is_alien'} && $fields->{'homeworld'}) {
	@values = (1, 2, 3, 4);
	@labels = ('Fight if Attacked', 'Make Demands', 'Attack If Defied', 'Attack Regardless');
    } elsif (!$ship1->{'is_alien'} || (defined($fields->{"do$suffix"}) && $fields->{"do$suffix"} eq '1')) {
	@values = (0, 1, 2, 3, 4);
	@labels = ('Flee', 'Fight if Attacked', 'Make Demands', 'Attack If Defied', 'Attack Regardless');
    } else {
	@values = (0, 2, 3, 4);
	@labels = ('Flee', 'Make Demands', 'Attack If Defied', 'Attack Regardless');
    }
    &print_option_list("do$suffix", \@values, \@labels, $fields, '');
}

sub print_demands {
    my ($suffix, $fields, $ship2) = @_;
    my @values = ('');
    my @labels = ('None', @{$ship2->{'modules'}});
    my $module;
    foreach $module (@{$ship2->{'modules'}}) {
	$module =~ /(\d+)|^([A-Z][a-z]+) /;
	push(@values, defined($1) ? $1 : $2);
    }
    print_option_list("dd$suffix", \@values, \@labels, $fields, ' size=5');
}

sub print_gifts {
    my ($suffix, $fields, $ship1) = @_;
    my @values = ('', -1);
    my @labels = ('None', 'Any one module', @{$ship1->{'modules'}});
    my $module;
    foreach $module (@{$ship1->{'modules'}}) {
	$module =~ /(\d+)|^([A-Z][a-z]+) /;
	push(@values, defined($1) ? $1 : $2);
    }
    print_option_list("dg$suffix", \@values, \@labels, $fields, ' size=5');
}

sub print_combat_strategy {
    my ($suffix, $fields, $ship1) = @_;
    my @values;
    my @labels;
    if ($ship1->{'is_alien'} && $fields->{'homeworld'}) {
	@values = (1);
	@labels = ('Favour Engines');
    } else {
	@values = (0, 1, 2, 3, 4, 5);
	@labels = ('Favour Fleeing', 'Favour Engines', 'Favour Weapons', 'Favour Shields', 'Favour Sensors', 'Favour Cloaks');
    }
    &print_option_list("dc$suffix", \@values, \@labels, $fields, '');
}

sub print_ideal_range {
    my ($suffix, $fields, $ship1) = @_;
    if (!$ship1->{'is_alien'} && !defined($fields->{"di$suffix"})) {
	$fields->{"di$suffix"} = $ship1->{'ideal_range'};
    }
    my @values = (0..$#ranges);
    my @labels = @ranges;
    if ($ship1->{'is_alien'}) {
	unshift(@values, -1);
	unshift(@labels, 'Random');
    }
    print_option_list("di$suffix", \@values, \@labels, $fields, '');
}

sub print_targetted {
    my ($suffix, $fields, $ship2) = @_;
    my @values = ('');
    my @labels = ('None', @{$ship2->{'modules'}});
    my $module;
    foreach $module (@{$ship2->{'modules'}}) {
	$module =~ /(\d+)|^([A-Z][a-z]+) /;
	push(@values, defined($1) ? $1 : $2);
    }
    print_option_list("dt$suffix", \@values, \@labels, $fields, ' size=5 multiple');
}

sub print_retreat_threshold {
    my ($suffix, $fields, $ship1) = @_;
    my @values;
    if ($ship1->{'is_alien'} && $fields->{'homeworld'}) {
	@values = (scalar(@{$ship1->{'modules'}}));
    } else {
	@values = (0..$#{$ship1->{'modules'}});
    }
    print_option_list("dr$suffix", \@values, \@values, $fields, '');
}

sub print_protected {
    my ($suffix, $fields, $ship1, $ship2) = @_;
    my @values = ('');
    my @labels = ('None', @{$ship1->{'modules'}});
    my $default = !defined($fields->{"dp$suffix"}) && $ship2->{'is_alien'};
    if ($default) {
	$fields->{"dp$suffix"} = '';
    }
    my $module;
    foreach $module (@{$ship1->{'modules'}}) {
	$module =~ /(\d+)|^([A-Z][a-z]+) /;
	my $j = defined($1) ? $1 : $2;
	push(@values, $j);
	if ($default && ($module =~ /^[A-Z]/ || $module !~ /\(U\)/) && $module !~ /^pod-/) {
	    $fields->{"dp$suffix"} .= "$j+"
	    }
    }
    if ($default) {
	$fields->{"dp$suffix"} =~ s/\+$//;
    }
    print_option_list("dp$suffix", \@values, \@labels, $fields, ' size=5 multiple');
}

sub print_torpedo_fire_rate {
    my ($suffix, $fields, $ship1) = @_;
    my @values;
    my @labels;
    my $i;
    for ($i = 0; $i * $i <= $ship1->{'torpedoes'}; $i++) {
	push(@values, $i);
	push(@labels, $i * $i . ' per round');
    }
    print_option_list("df$suffix", \@values, \@labels, $fields, '');
}

sub print_skill {
    my ($skill, $fields, $skill_name, $ship1) = @_;
    my @values;
    if (defined($fields->{"$skill"})) {
	@values = ($fields->{"$skill"});
    } else {
	$fields->{"$skill"} = &min($ship1->{'skills'}{$skill_name}, 64);
	@values = (0..64);
    }
    &print_option_list("$skill", \@values, \@values, $fields, '');
}

sub print_combat_tactics {
    my ($suffix, $ship1, $ship2, $turn, $ship_dir, $fields) = @_;
    print("<table border=1>\n");
    my $link = $ship1->{'name'};
    $link =~ s/ /%20/g;
    if (defined($ship1->{'url'})) {
	print("<tr><th colspan=2><h2><a href=\"$ship1->{'url'}\">$ship1->{'name'}</a></h2></th></tr>\n");
    } else {
	print("<tr><th colspan=2><h2><a href=\"http://janin.org/dow/shipconfig.cgi?$link\">$ship1->{'name'}</a></h2></th></tr>\n");
    }
    print("<tr align=center><th colspan=2>Higher Power Rank<input type=radio name=\"first\" value=\"$suffix\"");
    if ($ship1->{'power_rank'} > $ship2->{'power_rank'} || ($suffix eq '2' && $ship1->{'power_rank'} == $ship2->{'power_rank'})) {
	print(" checked");
    }
    print("></th></tr>\n");
    if ($ship1->{'is_alien'}) {
	print("<tr align=center><th colspan=2><input type=checkbox name=\"enemy\"");
	$ship1->{'name'} =~ /^([A-Z][a-z]+) \d+$/;
	if (defined($ship2->{'enemies'}{$1})) {
	    print(" checked");
	}
	print(">Enemy</input></th></tr>\n");
	print("<tr align=center><th colspan=2><input type=checkbox name=\"homeworld\"");
	if ($fields->{'homeworld'}) {
	    print(" checked");
	}
	print(">Homeworld Combat</input></th></tr>\n");
    } else {
	print("<tr align=center><th>Hidden Blessings</th><td>\n");
	my $blessing;
	foreach $blessing ('Id', 'Sn', 'Cl', 'Sh', 'Wp') {
	    print("<input type=checkbox name=\"$blessing$suffix\">$blessing</input>\n");
	}
	print("</td></tr>\n");
	print("<tr align=center><th>Total Engineering Skill</th>");
	&print_skill("eng_skill$suffix", $fields, 'Engineering', $ship1);
	print("</tr>\n");
	print("<tr align=center><th>Total Science Skill</th>");
	&print_skill("sci_skill$suffix", $fields, 'Science', $ship1);
	print("</tr>\n");
	&print_spells($suffix, $fields, $ship1, $ship2);
    }
    print("<tr align=center><th>Diplomatic Option</th>\n");
    print("<th>Demands</th></tr>\n");
    print("<tr align=center>");
    &print_diplomatic_option($suffix, $fields, $ship1);
    &print_demands($suffix, $fields, $ship2);
    print("</tr>\n");
    print("<tr align=center><th>Combat Strategy</th>");
    if (!$ship1->{'is_alien'}) {
	print("<th>Gifts</th>");
    }
    print("</tr>\n");
    print("<tr align=center>");
    &print_combat_strategy($suffix, $fields, $ship1);
    if (!$ship1->{'is_alien'}) {
	&print_gifts($suffix, $fields, $ship1);
    }
    print("</tr>\n");
    print("<tr align=center><th>Ideal Range</th>\n");
    print("<th>Targetted</th></tr>\n");
    print("<tr align=center>");
    &print_ideal_range($suffix, $fields, $ship1);
    &print_targetted($suffix, $fields, $ship2);
    print("</tr>\n");
    print("<tr align=center><th>Retreat Threshold</th>");
    if (!$ship1->{'is_alien'} && $ship1->{'shields'} > 0) {
	print("\n<th>Protected</th>");
    }
    print("</tr>\n");
    print("<tr align=center>");
    &print_retreat_threshold($suffix, $fields, $ship1);
    if (!$ship1->{'is_alien'}) {
	if ($ship1->{'shields'} > 0) {
	    &print_protected($suffix, $fields, $ship1, $ship2);
	}
	if ($ship1->{'torpedoes'} > 0) {
	    print("</tr>\n");
	    print("<tr align=center><th>Torpedo Fire Rate</th></tr>\n");
	    print("<tr align=center>");
	    &print_torpedo_fire_rate($suffix, $fields, $ship1);
	}
    }
    print("</tr>\n");
    print("</table>\n");
}

sub by_blessing {
    $blessing_order{$a} <=> $blessing_order{$b};
}

sub sort_blessings {
    my (@blessings) = @_;
    @blessings = sort(by_blessing @blessings);
    while (@blessings > 0 && $blessing_order{$blessings[0]} == -1) {
	shift(@blessings);
    }
    @blessings;
}

sub curse_fonts {
    my ($ship1, $factor) = @_;
    (defined($ship1->{'curses'}{$factor}) ? "<font color=$colors{'red'}>" : '', defined($ship1->{'curses'}{'Id'}) ? '</font>' : '');
}

sub print_factors {
    my ($ship1, $is_alien, $is_homeworld) = @_;
    print("<table border=1>\n");
    print("<tr><th colspan=4>$ship1->{'name'}</th></tr>\n");
    print("<tr align=center><th>Blessings</th><td colspan=3>", join(', ', sort_blessings(keys(%{$ship1->{'blessings'}}))), "</td></tr>\n");
    print("<tr align=center><th>Curses</th><td colspan=3><font color=$colors{'red'}>", join(', ', sort_blessings(keys(%{$ship1->{'curses'}}))), "</font></td></tr>\n");
    print("<tr><td></td><th>Normal</th><th>Bl / Fa</th><th>Bl &amp; Fa</th></tr>\n");
    my ($curse1, $curse2) = &curse_fonts($ship1, 'Id');
    print("<tr align=center><th>${curse1}Impulse$curse2</th><td>");
    if ($is_homeworld) {
    } elsif (!defined($ship1->{'blessings'}{'Id'})) {
	print("$curse1$ship1->{'factors'}{'Id'}%$curse2");
    } else {
	print("$curse1<em>$ship1->{'factors'}{'Id'}%</em>$curse2");
    }
    print("</td><td>$curse1");
    if ($is_homeworld && defined($ship1->{'blessings'}{'Id'})) {
	print("<em>", int($ship1->{'factors'}{'Id'} * 1.5), "%</em>");
    } else {
	print(int($ship1->{'factors'}{'Id'} * 1.5), "%");
    }
    print($curse2);
    if (!$ship1->{'is_alien'} || (defined($ship1->{'blessings'}{'Id'}))) {
	print("</td><td>$curse1", int(int($ship1->{'factors'}{'Id'} * 1.5) * 1.5), "%$curse2")
	}
    print("</td></tr>\n");
    ($curse1, $curse2) = &curse_fonts($ship1, 'Sn');
    print("<tr align=center><th>${curse1}Sensor$curse2</th><td>");
    if (!defined($ship1->{'blessings'}{'Sn'})) {
	print("$curse1$ship1->{'factors'}{'Sn'}%$curse2");
    }
    if (!$is_homeworld || defined($ship1->{'blessings'}{'Sn'})) {
	print("</td><td>$curse1", int($ship1->{'factors'}{'Sn'} * 1.5), "%$curse2");
    }
    if (!$is_homeworld && (!$ship1->{'is_alien'} || defined($ship1->{'blessings'}{'Sn'}))) {
	print("</td><td>$curse1", int(int($ship1->{'factors'}{'Sn'} * 1.5) * 1.5), "%$curse2");
    }
    print("</td></tr>\n");
    ($curse1, $curse2) = &curse_fonts($ship1, 'Cl');
    print("<tr align=center><th>${curse1}Cloak$curse2</th><td>");
    if (!defined($ship1->{'blessings'}{'Cl'})) {
	print("$curse1$ship1->{'factors'}{'Cl'}%$curse2");
    }
    if (!$is_homeworld || defined($ship1->{'blessings'}{'Cl'})) {
	print("</td><td>$curse1", int($ship1->{'factors'}{'Cl'} * 1.5), "%$curse2");
    }
    if (!$is_homeworld && (!$ship1->{'is_alien'} || defined($ship1->{'blessings'}{'Cl'}))) {
	print("</td><td>$curse1", int(int($ship1->{'factors'}{'Cl'} * 1.5) * 1.5), "%$curse2");
    }
    print("</td></tr>\n");
    ($curse1, $curse2) = &curse_fonts($ship1, 'Sh');
    print("<tr><th colspan=4>${curse1}Shields$curse2</th></tr>");
    print("<tr align=center><th>Total</th><td>$curse1");
    if (defined($ship1->{'blessings'}{'Sh'})) {
	print("<em>$ship1->{'shields'}</em>");
    } else {
	print($ship1->{'shields'});
    }
    print($curse2);
    if (!$is_homeworld || defined($ship1->{'blessings'}{'Sh'})) {
	print("</td><td>$curse1", int($ship1->{'shields'} * 1.5), $curse2);
    }
    if (!$ship1->{'is_alien'} || defined($ship1->{'blessings'}{'Sh'})) {
	print("</td><td>$curse1", int(int($ship1->{'shields'} * 1.5) * 1.5), $curse2);
    }
    print("</td></tr>\n<tr align=center><th>Per Module");
    my $i;
    my $print_note = 0;
    if ($is_alien && !$ship1->{'is_alien'} && $ship1->{'working_modules'} != 0) {
	$i = $ship1->{'working_modules'};
	if ($i != 0 && $ship1->{'working_modules'} != @{$ship1->{'modules'}} && $ship1->{'shields'} > 0) {
	    $print_note = $ship1->{'working_modules'};
	    print(' <a href="#note">[1]</a>');
	}
    } else {
	$i = @{$ship1->{'modules'}};
    }
    print('</th>');
    if ($i != 0) {
	print("<td>$curse1");
	if (defined($ship1->{'blessings'}{'Sh'})) {
	    print("<em>", int($ship1->{'shields'} / $i), "</em>");
	} else {
	    print(int($ship1->{'shields'} / $i));
	}
	print($curse2);
	if (!$is_homeworld || defined($ship1->{'blessings'}{'Sh'})) {
	    print("</td><td>$curse1", int($ship1->{'shields'} * 1.5 / $i), $curse2);
	}
	if (!$ship1->{'is_alien'} || defined($ship1->{'blessings'}{'Sh'})) {
	    print("</td><td>$curse1", int(int($ship1->{'shields'} * 1.5) * 1.5 / $i), $curse2);
	}
	print("</td>");
    }
    print("</tr>\n");
    ($curse1, $curse2) = &curse_fonts($ship1, 'Wp');
    print("<tr><th colspan=4>${curse1}Firepower$curse2</th></tr>\n");
    for ($i = 0; $i < @ranges; $i++) {
	print("<tr align=center><th>$ranges[$i]</th><td>$curse1");
	if ($ship1->{'firepower'}[$i] > 0) {
	    if (defined($ship1->{'blessings'}{'Wp'})) {
		print("<em>$ship1->{'firepower'}[$i]</em>");
	    } else {
		print($ship1->{'firepower'}[$i]);
	    }
	    print($curse2);
	    if (!$is_homeworld || defined($ship1->{'blessings'}{'Wp'})) {
		print("</td><td>$curse1", int($ship1->{'firepower'}[$i] * 1.5), $curse2);
	    }
	    if (!$ship1->{'is_alien'} || defined($ship1->{'blessings'}{'Wp'})) {
		print("</td><td>$curse1", int(int($ship1->{'firepower'}[$i] * 1.5) * 1.5), $curse2);
	    }
	}
	print("</td></tr>\n");
    }
    print("</table>\n");
    $print_note;
}

sub download_turn {
    my ($fields, $ship1) = @_;
    my $file = &get_page($Donor->{secreturl});
    if (!defined($file)) {
	return 0;
    }
    &strip_spaces($file);
    if ($file =~ /<P><TABLE BORDER=1>(?:<TBODY>)?<TR><TH>Engineering skills \((\d+) = \d+\+\d+\)<\/TH><TH>Science Skills \((\d+) = \d+\+\d+\)<\/TH>.*?<\/TABLE>/i) {
	$fields->{'eng_skill1'} = $1;
	$fields->{'sci_skill1'} = $2;
	my $list = $&;
	if ($list =~ /<TR ALIGN=CENTER><TD>Enlightenment<\/TD>/i) {
	    $ship1->{'Enlightenment'}{'Engineering'} = 1;
	}
	if ($list =~ /<TR ALIGN=CENTER><TD>[^<]*<\/TD><TD>Enlightenment<\/TD>/i) {
	    $ship1->{'Enlightenment'}{'Science'} = 1;
	}
    }
    if ($file =~ /<H3>Religious Favour<\/H3>((?:<BR>You are one of The \w+ One\'s Chosen)+)?<LI>Engineering: (\d+)<LI>Science: (\d+)<LI>Medical: (\d+)<LI>Weaponry: (\d+)</i) {
		$ship1->{'favor'} = {
			'Engineering' => $2,
			'Science' => $3,
			'Medical' => $4,
			'Weaponry' => $5,
		};
		if (defined($1)) {
			my $chosen = $1;
			my %lookup = (
				'Mighty' => 'Engineering',
				'Wise' => 'Science',
				'Merciful' => 'Medical',
				'Fierce' => 'Weaponry',
			);
			while ($chosen =~ /<BR>You are one of The (\w+) One\'s Chosen/ig) {
	$ship1->{'favor'}{$lookup{$1}} = 200;
    }
					 }
    }
    if ($file =~ /<SELECT NAME="dd" SIZE=5>.*?<\/SELECT>/i) {
	my $list = $&;
	while ($list =~ /<OPTION VALUE=(\d+)(?: SELECTED)?>([A-Z][a-z]+)/g) {
	    $artifact_lookup{$1} = $2;
	}
    }
    if ($file =~ /<SELECT NAME="dg" SIZE=5 MULTIPLE>.*?<\/SELECT>/i) {
	my $list = $&;
	while ($list =~ /<OPTION VALUE=(\d+)(?: SELECTED)?>([A-Z][a-z]+)/g) {
	    $artifact_lookup{$1} = $2;
	}
    }
    1;
}

sub download_orders {
    my ($fields) = @_;
    my $orders_page_url = $Donor->{secreturl};
    $orders_page_url =~ s/\.htm$/.ord/;
    my $orders_page = &get_page($orders_page_url);
    if (!defined($orders_page)) {
	return 0;
    }
    my %orders;
    while ($orders_page =~ /^([^=\n]+)=([^\n]*)/gm) {
	if (defined($artifact_lookup{$2})) {
	    $orders{"${1}1"} .= "$artifact_lookup{$2}+";
	} else {
	    $orders{"${1}1"} .= "$2+";
	}
    }
    my $order;
    foreach $order (keys(%orders)) {
	$orders{$order} =~ s/\.\+//g;
	$orders{$order} =~ s/\+$//;
	$fields->{$order} = $orders{$order};
    }
    1;
}

sub print_warnings {
    my ($ship1, $ship2, $fields) = @_;
    if ($ship2->{'is_alien'} && defined($fields->{'homeworld'}) && $fields->{'homeworld'} && $ship2->{'name'} =~ /^([A-Z][a-z]+) \d+$/ && defined($ship1->{'enemies'}{$1})) {
	print("<p>Warning: Alien explosion damage can sometimes exceed the expected amount.  While the simulator does attempt to take this into account, it is an as yet poorly understood effect.</p>\n");
    }
    if ($ship2->{'is_alien'} && (!defined($fields->{'homeworld'}) || !$fields->{'homeworld'})) {
	print("<p>Warning: How aliens select ideal range and retreat threshold is not known, so you might want to try various settings for them to see how things might go.  The default settings are randomly selected: for ideal range, from any range the alien has a weapon for, for retreat threshold, from 1 to one less than the number of modules on the alien ship.</p>\n");
    }
    my @ship1_curses = sort_blessings(keys(%{$ship1->{'curses'}}));
    my @ship2_curses = sort_blessings(keys(%{$ship2->{'curses'}}));
    if (@ship1_curses > 0 || @ship2_curses > 0) {
	print("<p>Warning: Effects of <font color=$colors{'red'}>curses</font> <strong>not</strong> included in the ship factor listing below.  Cursed factors will be halved, until the cursed artifact is uncursed or shot off.</p>\n");
    }
}

sub print_combat_form {
    my ($ship1, $ship2, $fields, $ship_dir) = @_;
    print("<form action=\"fight.cgi\" method=\"POST\">\n");
    print("<input name=ship1 value=\"");
    if (defined($ship1->{'url'})) {
	print($ship1->{'url'});
    } else {
	print($ship1->{'name'});
    }
    print("\" type=hidden>\n");
    print("<input name=ship2 value=\"");
    if (defined($ship2->{'url'})) {
	print($ship2->{'url'});
    } else {
	print($ship2->{'name'});
    }
    print("\" type=hidden>\n");
    print("<input name=terrain value=\"$fields->{'terrain'}\" type=hidden>\n");
    if (defined($ship1->{'turn'})) {
	print("<input name=turn1 value=\"$ship1->{'turn'}\" type=hidden>\n");
    }
    if (defined($ship2->{'turn'})) {
	print("<input name=turn2 value=\"$ship2->{'turn'}\" type=hidden>\n");
    }
    print("<input type=hidden name=dow_pw value=\"$Donor->{dow_pw}\">\n");
    print("<input type=submit value=\"Make It So\">\n");
    print("<input type=reset>\n");
    print("Runs<select name=\"runs\">\n");
    print("<option value=1>1</option>\n");
    print("<option value=100 selected>100</option>\n");
    print("<option value=1000>1,000</option>\n");
    print("<option value=10000>10,000</option>\n");
    print("</select>\n");
    print("Terrain: $fields->{'terrain'}\n");
    print("<input type=checkbox name=\"loot_colors\" checked>Color-coded Loot</input>\n");
    print("<input type=checkbox name=\"debug\">Debugging Output</input>\n<p>");
    &print_warnings($ship1, $ship2, $fields);
    if (!defined($fields->{'homeworld'})) {
	$fields->{'homeworld'} = 0;
    }
    print("<table>\n");
    print("<tr><td>\n");
    my $print_note = &print_factors($ship1, $ship2->{'is_alien'}, 0);
    print("</td><td>");
    &print_factors($ship2, $ship2->{'is_alien'}, $fields->{'homeworld'});
    print("</td></tr>\n");
    if ($print_note) {
	print("<tr><td colspan=2><a name=note>[1]</a> Specifically, amount of shielding per artifact and working non-pod module ($print_note, in this case).</td></tr>\n");
    }
    print("<tr><td valign=top>\n");
    &print_combat_tactics('1', $ship1, $ship2, $ship1->{'turn'}, $ship_dir, $fields);
    print("</td><td valign=top>");
    &print_combat_tactics('2', $ship2, $ship1, $ship2->{'turn'}, $ship_dir, $fields);
    print("</td></tr>\n");
    print("</table>\n");
    print("<input type=submit value=\"Make It So\">\n");
    print("</form>\n");
}

sub print_page_header {
    print("Content-type: text/html\n\n");
    print("<html>\n<head>\n<title>Combat Simulator: Combat Settings</title>\n</head>\n");
    print("<body text=\"yellow\" bgcolor=\"black\" link=\"white\" vlink=\"cyan\">\n");
    print("<p><blink>Warning!</blink> The combat simulator has not been updated to any of the new combat rules. Use with caution!\n");
    print("<h2>Combat Simulator: Combat Settings</h2>\n");
}

sub print_page {
    my ($ship1, $ship2, $fields, $ship_dir) = @_;
    &print_combat_form($ship1, $ship2, $fields, $ship_dir);
    print("<!-- ", $ENV{'QUERY_STRING'}, " -->\n");
    print("</body>\n</html>\n");
}

my $ship_dir = '/Path/to/ships';

if (!defined($ENV{'QUERY_STRING'}) || $ENV{'QUERY_STRING'} eq '') {
    $ENV{'QUERY_STRING'} = join('', <STDIN>);
}

my $fields = &extract_fields($ENV{'QUERY_STRING'});
if (!defined($fields->{'turn1'}) || $fields->{'turn1'} !~ /^[0-9]+$/) {
    $fields->{'turn1'} = SelectOne("select max(turn) from shipconfig where ship=?;", 
				   $fields->{ship1});
}
if (!defined($fields->{'turn2'}) || $fields->{'turn2'} !~ /^[0-9]+$/) {
    $fields->{'turn2'} = SelectOne("select max(turn) from shipconfig where ship=?;",
				   $fields->{ship2});
}

&print_page_header;
my $ship1 = &read_ship($fields->{'ship1'}, $fields->{'turn1'}, $ship_dir);
my $ship2 = &read_ship($fields->{'ship2'}, $fields->{'turn2'}, $ship_dir);


#print "ship1=$fields->{ship1}, ship2=$fields->{ship2}, turn1=$fields->{turn1}, turn2=$fields->{turn2}, shipdir = $ship_dir\n";

if (!defined($ship1) || !defined($ship2)) {
    herror("Failed to load ships.");
}

# If we're simulating the existing pairing, use orders.
if ($Donor->{ship} eq $ship1 && $ship2 eq PairedShip($Donor->{ship}, SelectOne("select max(turn) from turnupdate;"))) {
    if (!&download_turn($fields, $ship1)) {
	herror("Could not download turn page.");
    }
    if (!&download_orders($fields)) {
	herror("Could not download orders page.");
    }
}

&print_page($ship1, $ship2, $fields, $ship_dir);
