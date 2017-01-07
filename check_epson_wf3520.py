#!/usr/bin/env python

# Check Epson WF-3520 cartidges status
# Written by Eric Viseur <eric.viseur@gmail.com>, 2017
# Released under MIT license 

# v1.0 - Initial release

import sys
import errno
import urllib2
from optparse import OptionParser

# ---- constants ---------------------------------------------------------------

HOST = 'localhost'
PORT = 80
WARNING = 15
CRITICAL = 10

about_info = {
  "name"           : r"check_epson_wf3520.py Nagios plugin",
  "product_number" : r"N/A",
  "version"        : r"1.0",
}

# ---- check the cartidges status ----------------------------------------------

def check_cartidges():

  try:
    response = urllib2.urlopen('http://' + options.host + ':' + str(options.port) + '/PRESENTATION/HTML/TOP/PRTINFO.HTML')
    html = response.read()
    for line in html.splitlines():
      if "Ink_K.PNG" in line:
        black = 100 * float(line.split("height='", 1)[-1].replace("'>", "")) / 50
      if "Ink_M.PNG" in line:
        magenta = 100 * float(line.split("height='", 1)[-1].replace("'>", "")) / 50
      if "Ink_Y.PNG" in line:
        yellow = 100 * float(line.split("height='", 1)[-1].replace("'>", "")) / 50
      if "Ink_C.PNG" in line:
	cyan = 100 * float(line.split("height='", 1)[-1].replace("'>", "")) / 50
      if "Ink_Waste.PNG" in line:
        waste = 100 * float(line.split("height='", 1)[-1].replace("'>", "")) / 50

    if black < options.warning or magenta < options.warning or yellow < options.warning or cyan < options.warning or waste < options.warning: status = 'WARNING'
    elif black < options.critical or magenta < options.critical or yellow < options.critical or cyan < options.critical or waste < options.critical: status = 'CRITICAL' 
    else: status = 'OK'
    s = 'Black: %s%%, Magenta: %s%%, Yellow: %s%%, Cyan: %s%%, Waste container: %s%%|black=%s;%d;%d;; magenta=%s;%d;%d;; yellow=%s;%d;%d;; cyan=%s;%d;%d;; waste=%s;%d;%d;;' % (black, magenta, yellow, cyan, waste, black, options.warning, options.critical, magenta, options.warning, options.critical, yellow, options.warning, options.critical, cyan, options.warning, options.critical, waste, options.warning, options.critical)
  except:
    status = 'CRITICAL'
    s = 'Cannot check cartidges status'

  return(status, s)

# ---- create the command line options -----------------------------------------

def create_options():
  parser = OptionParser()

  parser.add_option("-H", "--host", type = "string",
    dest = "host", action = "store", default = HOST,
    help = ("Printer IP address. Default [%s]" % HOST))

  parser.add_option("-p", "--port", type = "int",
    dest = "port", action = "store", default = PORT,
    help = ("Listening port of the printer web server. Default [%d]" % PORT))

  parser.add_option("-w", "--warning", type = "int",
    dest = "warning", action = "store", default = WARNING,
    help = ("Warning threshold. Default [%d]" % WARNING))

  parser.add_option("-c", "--critical", type = "int",
    dest = "critical", action = "store", default = CRITICAL,
    help = ("Critical threshold. Default [%d]" % CRITICAL))

  (options, args) = parser.parse_args()
  return [options, args]

# ---- global variables --------------------------------------------------------

(options, args) = create_options()

################################################################################
#
#                               m a i n l i n e
#
################################################################################

status, comment=check_cartidges()

print ('%s - %s' % (status, comment))
if status[0:1] == 'O': exit(0)
elif status[0:1] == 'W': exit(1)
else: exit(2)
