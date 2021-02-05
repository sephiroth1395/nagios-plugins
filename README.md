# nagios-plugins

- [nagios-plugins](#nagios-plugins)
  - [Overview](#overview)
  - [Plugins](#plugins)
    - [check_epson_wf3520](#check_epson_wf3520)
      - [Description](#description)
      - [Usage](#usage)
    - [check_dyndns](#check_dyndns)
      - [Description](#description-1)
      - [Usage](#usage-1)
    - [check_voo](#check_voo)
      - [Description](#description-2)
      - [Usage](#usage-2)

## Overview

This repo contains Nagios plugins that I've either written from scratch or adapted from pre-existing scripts to suit my needs.

## Plugins

### check_epson_wf3520
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

### check_voo
#### Description
This plugin parses the HTML output of the Voo modem web interface and extracts the SNR (Signal to Noise) information for all the downtream channels. It can be useful to track connectivity issues as well as monitor the impact of works on your line.

I can only check it with the Technicolor as it is the one I have but it is my understanding the WebUI is the same on the Netgear modems, so it should work. If that's not the case, I'm happy to assist to make it more universal.

Always check github for the latest release.

#### Usage

```
usage: check_voo.py [-h] [-H MODEMADDRESS] [-c CONFIGFILE] [--perfdata] [-v]

Nagios-compliant plugin to check the connectivity status on a VOO Technicolor modem in bridge mode

optional arguments:
  -h, --help            show this help message and exit
  -H MODEMADDRESS, --host MODEMADDRESS
                        IP address of the VOO modem. Default [192.168.100.1]
  -c CONFIGFILE, --config-file CONFIGFILE
                        Configuration file location Default [check_voo.yml]
  --perfdata            Append perfdata to the plugin output.
  -v, --verbose         Produce verbose output.

The configuration file is expected to present the following contents:

login: 
password: 
```
