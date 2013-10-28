#!/usr/bin/perl -w

use strict;
use Image::Magick;

my($Width, $Height, $Size, $FGColor, $BGColor, $Points);

$Width = shift || 16;
$Height = shift || 16;
$FGColor = shift || 'red';
$BGColor = shift || 'white';

$Size = $Width . "x" . $Height;
$Points = ($Width/2) . "," . ($Height/2) . " " . ($Width/2) . "," . ($Height-1);


#print "Content-type: text/plain\n\n";
#print "xc:$BGColor, $FGColor, $Points\n";
#exit;

my $image=Image::Magick->new(size=>$Size);
$image->ReadImage("xc:$BGColor");

$image->Draw(fill=>$FGColor,
	primitive=>'circle', 
	points=>$Points,
	stroke=>$BGColor);

print "Content-type: image/png\n\n";

binmode STDOUT;
$image->Write('png:-');  
