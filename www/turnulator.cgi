#!/usr/bin/perl -w
use strict;
use LWP::Simple;
use Getopt::Std;
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
    herror("Usage: turnulator.cgi");
}

sub GeneratePage {
    my($pageurl, $page, $ordurl, $ord, %orders, @turn);
    $pageurl = $Donor->{secreturl};
    if ($pageurl !~ m|^http://tbg.fyndo.com|) {
	herror("Sorry, I need your secret URL to run the turnulator");
    }
    if ($pageurl =~ m|^http://tbg.fyndo.com/share_|) {
	herror("Sorry, you cannot use the turnulator with a 'share' secret URL. You must use your full, 'turn' secret URL.");
    }
    $page = get($pageurl);
    if ($page =~ /^\s*$/) {
	herror("Can't retrieve turn page from \"$pageurl\". Try again later.");
    }
    $ordurl = $pageurl;
    $ordurl =~ s/\.htm$/.ord/;
    $ord = get($ordurl);
    @turn = split(/^/m, $page);
    %orders = &interpret_orders($ord);
    if (keys(%orders) > 0) {
	merge_orders(\%orders, @turn);
    }
    remove_javascript(@turn);
    add("Content-type: text/html\n\n");
    add(@turn);
    add("<P>Debug: $pageurl $ordurl<p>");
}

sub interpret_orders {
    my ($orders_page) = @_;
    my %orders;
    if (defined($orders_page)) {
	while ($orders_page =~ /^([^=\n]+)=([^\n]*)/gm) {
	    push(@{$orders{$1}}, $2);
	}
    }
    return %orders;
}

sub remove_javascript {
    my $i;
    for ($i = 0; $i < @_; $i++) {
	if ($_[$i] =~ /<\/HTML>/i) {
	    splice(@_, $i + 1);
	}
    }
}

sub merge_orders {
    my $orders = shift(@_);
    my $is_continued;
    my $is_multiple;
    my $name;
    my $selected;
    my $line;
    foreach $line (@_) {
	if (defined($is_continued)) {
	    $line =~ s/^[^\"]*\"//;
	    $is_continued = undef;
	}
	$line =~ s/ SELECTED>/>/i;
	if ($line =~ /<SELECT NAME=\"([^\"]+)\"/i) {
	    $name = $1;
	    $is_multiple = $line =~ /MULTIPLE/i;
	    if (defined($orders->{$name})) {
		$selected = shift(@{$orders->{$name}});
	    } else {
		$selected = undef;
	    }
	} elsif ($line =~ /<OPTION VALUE=[\" ]?([^\s>\"]+)\"?\s*>/i) {
	    my $option = $1;
	    if (defined($selected) && $selected eq $option) {
		$line =~ s/VALUE=[\" ]?\Q$option\E\"?\s*>/VALUE=$option SELECTED>/i;
		if ($is_multiple && defined($orders->{$name})) {
		    $selected = shift(@{$orders->{$name}});
		}
	    }
	} elsif ($line =~ /<INPUT [^>]*NAME=\"([^\"]+)\"/i) {
	    $name = $1;
	    if (defined($orders->{$name})) {
		$selected = shift(@{$orders->{$name}});
		if (defined($selected)) {
		    $selected =~ s/\"/&quot;/g;
		    $selected =~ s/</&lt;/g;
		    $selected =~ s/>/&gt;/g;
		    if ($line =~ s/VALUE=\"[^\"]*\"/VALUE=\"$selected\"/i) {
		    } elsif ($line =~ s/VALUE=\"[^\"]*$/VALUE=\"$selected\"/i) {
			$is_continued = 1;
		    } else {
			$line =~ s/(<INPUT [^>]*)>/$1 VALUE=\"$selected\">/i;
		    }
		}
	    }
	}
    }
}
