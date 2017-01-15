#!/usr/bin/perl -w

#######################################################################
#
# Copyright (c) 2007 Jaime Gascon Romero <jgascon@gmail.com>
# Additional features by Eric Viseur <eric.viseur@gmail.com>
#
# License Information:
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# $Id: check_openvpn.pl,v 1.1 2017/01/08 12:00:00 jgr Exp jgr $
# $Revision: 1.1 $
# Home Site: http://emergeworld.blogspot.com/
# Home Site: http://github.com/ev1z/
#
# Changelog
#   v1.0 	20070715	Initial release from Jaime Gascon Romero
#   v1.1	20170107	Several improvements made on code
#   				- Code structure adapted to parse the
#   				  telnet output only once
#   				- Removed the -w|--warning unsused
#   				  argument
#   				- Server version output with -v
#   				- perfdata with --perfdata
#   				- Removed the use of utils.pm as it
#   				  created issues with CentOS 7
# #####################################################################

use diagnostics;
use strict;
use Net::Telnet ();
use Getopt::Long qw(:config no_ignore_case);
use vars qw($PROGNAME $VERSION);

$PROGNAME = "check_openvpn";
$VERSION = '$Revision: 1.1 $';

$ENV{'PATH'}='';
$ENV{'BASH_ENV'}=''; 
$ENV{'ENV'}='';

my ($opt_h, $opt_H, $opt_p, $opt_P, $opt_t, $opt_i, $opt_n, $opt_c, $opt_C, $opt_r, $opt_v, $opt_perfdata);

sub print_help ();
sub print_usage ();

GetOptions
  ("h"  =>  \$opt_h, "help" => \$opt_h,
   "H=s" => \$opt_H, "host=s"  => \$opt_H,
   "p=i" => \$opt_p, "port=i" => \$opt_p,
   "P=s" => \$opt_P, "password=s" => \$opt_P,
   "t=i" => \$opt_t, "timeout=i" => \$opt_t,
   "i"  =>  \$opt_i, "ip" => \$opt_i,
   "n" => \$opt_n, "numeric" => \$opt_n,
   "c" => \$opt_c, "critical" => \$opt_c,
   "C=s" => \$opt_C, "common_name=s" => \$opt_C,
   "r=s" => \$opt_r, "remote_ip=s" => \$opt_r,
   "v" => \$opt_v, "version" => \$opt_v,
   "perfdata" => \$opt_perfdata,
  ) or exit 3;

# default values
unless ( defined $opt_t ) {
  $opt_t = 10;
}

if ($opt_h) {print_help(); exit 0;}

if ( ! defined($opt_H) || ! defined($opt_p) ) {
  print_usage();
  exit 3
}

my @lines;
my @clients;
my @clients_ip;
my $output = "";
my $perfdata = "";
my $t;

eval { 
  $t = new Net::Telnet (Timeout => $opt_t,
                        Port => $opt_p,
                        Prompt => '/END$/'
                       );
  $t->open($opt_H);
  if ( defined $opt_P ) {
    $t->waitfor('/ENTER PASSWORD:$/');
    $t->print($opt_P);
  }
  $t->waitfor('/^$/');
  @lines = $t->cmd("status 2");
  $t->close;
};

if ($@) {
  print "OpenVPN Critical: Can't connect to server\n";
  exit 2;
}

# Parse the return of the status 2 command
foreach (@lines) {
  # OpenVPN version
  if ($_ =~ /TITLE,.*/ && defined $opt_v) {
    $_ =~ s/TITLE,//;
    $output .= "  "."$_".".";
  }
  # Build the connected clients array
  if ($_ =~ /CLIENT_LIST,.*,(\d+\.\d+\.\d+\.\d+):\d+,/) {
    push @clients_ip, $1;
  }
  if ($_ =~ /CLIENT_LIST,(.*),\d+\.\d+\.\d+\.\d+:\d+,/) {
    push @clients, $1;
  }
}

# Specific client IP address is to be checked
if (defined $opt_r) {
  if ( ! grep /\b$opt_r\b/, @clients_ip) {
    if (defined $opt_c) {
      print "OpenVPN CRITICAL: $opt_r not connected.";
      exit 2;
    } else {
      print "OpenVPN WARNING: $opt_r not connected.";
      exit 1;
    }
  }
}

# Specific client CN is to be checked
if (defined $opt_C) {
  if ( ! grep /\b$opt_C\b/, @clients) {
    if (defined $opt_c) {
      print "OpenVPN CRITICAL: $opt_C not connected.";
      exit 2;
    } else {
      print "OpenVPN WARNING: $opt_C not connected.";
      exit 1;
    }
  }
}

# Display only the amount of connected clients
if (defined $opt_n && ! defined $opt_i) {
  $output .= "  ".@clients." connected clients.";
# Display the amount of connected clients and their IP addresses
} elsif (defined $opt_n && defined $opt_i) {
  $output .= "  ".@clients." connected clients: ".@clients_ip.".";
# Display only the IP addresses of the clients
} elsif (! defined $opt_n && defined $opt_i) {
  $output .= "  Connected clients: ".@clients_ip.".";
}

# Perfdata
if (defined $opt_perfdata) {
  if (defined $opt_n) {
    $perfdata .= "'Connected clients'=".@clients.";;;;,";
  }
}

print "OpenVPN OK."."$output"."|"."$perfdata";
exit 0;

#######################################################################
###### Subroutines ####################################################

sub print_usage() {
  print "Usage: $PROGNAME -H | --host <IP or hostname> -p | --port <port number> [-P | --password] <password> [-t | --timeout] <timeout in seconds> [-i | --ip] [-n | --numeric] [-C | --common_name] <common_name> [-r | --remote_ip] <remote_ip> [-c | --critical] [-w | --warning] [-v | --version]\n\n";
  print "       $PROGNAME [-h | --help]\n";
}

sub print_help() {
  print "$PROGNAME $VERSION\n\n";
  print "Written by Eric Viseur based on code by Jaime Gascon Romero
Released under MIT license

Nagios plugin to check the clients connected to a openvpn server.

";
  print_usage();
  print "
-H | --host\tIP address or hostname of the openvpn server.
-p | --port\tManagement port interface of the openvpn server.
-P | --password\tPassword for the management interface of the openvpn server.
-t | --timeout\tTimeout for the connection attempt. Optional, default 10 seconds.

  Optional parameters
  ===================

-i | --ip\tPrints the IP address of the remote client instead of the common name.
-n | --numeric\tPrints the number of clients connected to the OpenVPN server.
-v | --version\tPrint the version of the OpenVPN server.

  Matching Parameters
  ===================

-C | --common_name\tThe common name, as it is specified in the client certificate, who is wanted to check.
-r | --remote_ip\tThe client remote ip address who is wanted to check.
-c | --critical\tExits with CRITICAL status if the client specified by the common name or the remote ip address is not connected.

  Other Parameters
  ================

-h | --help\tShow this help.
";

}

# vim:sts=2:sw=2:ts=2:et
