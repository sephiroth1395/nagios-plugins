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
