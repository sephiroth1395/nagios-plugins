#!/usr/bin/perl 
#
# $Id: check_entropy.pl 384 2014-05-20 13:16:55Z phil $
#
# program: check_entropy
# author, (c): Philippe Kueck <projects at unixadm dot org>
#
# From Nagios Exchange
# https://www.unixadm.org/software/nagios-stuff/checks/check_entropy

use strict;
use warnings;
use Getopt::Long;
use Pod::Usage;

my ($warn, $crit, $entropy, $exit) = (0, 0, 0, 0);
sub nagexit {
	my $exitc = {0 => 'OK', 1 => 'WARNING', 2 => 'CRITICAL', 3 => 'UNKNOWN'};
	printf "%s - %s\n", $exitc->{$_[0]}, $_[1];
	exit $_[0]
}

Getopt::Long::Configure("no_ignore_case");
GetOptions(
	'H=s' => sub {},
	'w=i' => \$warn,
	'c=i' => \$crit,
	'h|help' => sub {pod2usage({'-exitval' => 3, '-verbose' => 2})}
) or pod2usage({'-exitval' => 3, '-verbose' => 0});

pod2usage({'-exitval' => 3, '-verbose' => 0}) unless $warn && $crit;


open FILE, "< /proc/sys/kernel/random/entropy_avail" or nagexit 3, $!;
($entropy) = <FILE> =~ /^(\d+)$/;
close FILE;
$exit = 2 if $exit < 2 && $entropy < $crit;
$exit = 1 if $exit < 1 && $entropy < $warn;
nagexit $exit, sprintf "available entropy is %d|'entropy'=%d;%d;%d;0",
	$entropy, $entropy, $warn, $crit

__END__

=head1 NAME

check_entropy

=head1 VERSION

$Revision: 384 $

=head1 SYNOPSIS

 check_entropy [-H HOST] [-w WARN] [-c CRIT]

=head1 OPTIONS

=over 8

=item B<H>

Dummy for compatibility with Nagios.

=item B<w>

Warn when available entropy drops below this threshold.

=item B<c>

Return critical state when available entropy drops below this threshold.

=back

=head1 DESCRIPTION

This nagios/icinga check script checks the available entropy. It also returns the perfdata.

=head1 DEPENDENCIES

=over 8

=item C<Getopt::Long>

=item C<Pod::Usage>

=back

=head1 AUTHOR

Philippe Kueck <projects at unixadm dot org>

=cut
