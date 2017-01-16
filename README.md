# nagios-plugins

## Overview

This repo contains Nagios plugins that I've either written from scratch or adapted from pre-existing scripts to suit my needs.

## Plugins

### check_epson_wf3520.pl
#### Description
This plugin is designed specifically for the Epson WF-3520 multifunction printer.  It may or may not work with other Epson printers with adaptations.  I'm more than happy to adapt it based on pull requests to cover more devices.
It fetches the status of the 4 ink cartridges and the waste container by parsing the contents of the device's web interface.

This plugin requires the *urllib2* python module.

#### Usage

Just drop the script on your monitoring server and invoke it with the printer IP address:
```
Usage: check_epson_wf3520.py [options]

Options:
  -h, --help            show this help message and exit
  -H HOST, --host=HOST  Printer IP address. Default [localhost]
  -p PORT, --port=PORT  Listening port of the printer web server. Default [80]
  -w WARNING, --warning=WARNING
                        Warning threshold. Default [15]
  -c CRITICAL, --critical=CRITICAL
                        Critical threshold. Default [10]
```

### check_dyndns
#### Description
This plugin checks if the provided dynamic DNS hostname matches the current public IPv4 address of the host that runs the plugin.  It can optionally attempt to restart ddclient if there is a mismatch.

This last feature requires that nrpe can launch command as *sudo*.  This can have sudoers and SELinux implications, depending on the distribution you're using.

This plugin requires *wget* and the Nagios *check_dns* plugin.
If you're a CentOS/RHEL user and have SELinux enabled, you may need an additional SELinux policy to allow NRPE to invoke wget and do HTTP requests.  The *check_dyndns.te* file contains a policy that will allow that specific action.

#### Usage

```
  Use: /usr/lib64/nagios/plugins/check_dyndns -H host [ -s dns server ] [ -r ]

  -H|--host     Hostname to check
  -s|--server   DNS server to use.  Default: 8.8.8.8
  -r|--restart  Attempt a ddclient service restart if there is an IP/name mismatch
```
