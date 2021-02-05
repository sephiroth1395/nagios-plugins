#!/usr/bin/env python3

# Nagios-compliant plugin to check the connectivity status on a 
# VOO (Belgian ISP) Technicolor modem.
# Written by Eric Viseur <eric.viseur@gmail.com>, 2021
# Released under MIT license

import mechanize
import array
from lxml import etree
from argparse import ArgumentPaser

###
# Variables
vooLogin="voo"
vooPassword="QYBPMGGJ"
###


# ---- constants --------------------------------------------------------------

HOST_ADDRESS = '192.168.100.1'
CONFIG_FILE = 'checyk_voo.yml'

# ---- parse the arguments ----------------------------------------------------

def create_args():
  parser = ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      description = 'Nagios-compliant plugin to check the connectivity status on a VOO Technicolor modem in bridge mode',
      epilog = 'zgeg.'
      )

  parser.add_argument("-H", "--host", action = "store",
    dest = 'modemAddress', default = HOST_ADDRESS,
    help = ("IP address of the VOO modem. Default [%s]" % HOST_ADDRESS))

  parser.add_argument("-c", "--config-file", action = "store",
    dest = 'configFile', default = CONFIG_FILE,
    help = ("Configuration file location Default [%s]" % CONFIG_FILE))

# TODO: Add footer with the configuration file structure

  parser.add_argument("--perfdata", action = 'store_true',
    help = 'Append perfdata to the plugin output.')

  parser.add_argument("-v", "--verbose", action = 'store_true',
    help = 'Produce verbose output.')

  args = parser.parse_args()
  return args

# ---- parse the configuration file -------------------------------------------

def parse_config(configFile):

  # Check if the config file exists
  if os.path.exists(configFile):
    # Attempt to read the config file contents
    try:
      stream = open(configFile, 'r')
      settings = yaml.load(stream, Loader=yaml.BaseLoader)
      vooLogin = settings['login']
      vooPassword = settings['password']
      return(vooLogin, vooPassword)
    except:
      print("CRITICAL - Error reading the configuration file %s" % configFile)
      exit(2)
  else:
    print("CRITICAL - Configuration file %s does not exist" % configFile)
    exit(2)

# ---- main routine -----------------------------------------------------------
# ---- This plugin leverages the mechanize python module to mimic the      ----
# ---- behaviour of a human user.  Sorry for the messy code but the        ----
# ---- WebUI HTML output is a mess in itself                               ----
# -----------------------------------------------------------------------------

args = create_args()
(vooLogin, vooPassword) = parse_config(args.configFile)

br = mechanize.Browser()

# Login to the modem
try:
    br.set_handle_robots(False)
    br.addheaders = [('User-agent', 'Mozilla/5.0')]
    br.open('http://' + args.modemAddress + '/')
    br.select_form(name="login")
    br.set_value(vooLogin,"loginUsername")
    br.set_value(vooPassword,"loginPassword")
    br.submit()
except:
    print("UNKNOWN - Cannot login to modem")
    exit(3)

# Go to the connection statistics page
try:
    br.open("http://192.168.100.1/RgConnect.asp")
except:
    print("UNKNOWN - Cannot open connection info")
    exit(3)

# Transform the response into an XML structure
connInfo = mechanize._html.content_parser(br.response())

# Move into the XML structure
connInfoContent = connInfo[1][0][4][2][3]
connInfoGeneral = connInfoContent[0][0][1][0][2][2][0]
connInfoDownstream = connInfoContent[0][0][1][0][2][4][0]
connInfoUpstream = connInfoContent[0][0][1][0][2][6][0]

# Extract general connection info and cleanup
downAcquired = connInfoGeneral[2][2][0].text
downAcquired = downAcquired.strip('i18n("')
downAcquired = downAcquired.strip('")')

connectionState = connInfoGeneral[3][1][0].text
connectionState = connectionState.strip('i18n("')
connectionState = connectionState.strip('")')

if downAcquired == "Locked":
    if connectionState == "OK":
        
        perfdata = ""

        # Starting with Element 2, connInfoDownstream contains each downstream channel
        for i in range(2, 18):
            j = i-1
            modulation = connInfoDownstream[i][2].text
            baudrate = connInfoDownstream[i][4].text
            power = connInfoDownstream[i][6].text.lstrip()
            power = power.replace(" dBmV","")
            snr = connInfoDownstream[i][7].text.lstrip()
            snr = snr.replace(" dB","")
            
            perfdata += "'down_" + str(j) + "_pwr'=" + power + ";;;; 'down_" + str(j) + "_snr'=" + snr + ";;;; "

        if args.verbose:            
            verboseData += 'Downstream channels info'
            for i in downChannels:
                verboseData += i
            
        # Starting with Element 2, connInfoUpstream contains each downstream channel
        for i in range(2, 6):
            j = i-1
            modulation = connInfoUpstream[i][2].text
            baudrate = connInfoUpstream[i][4].text
            power = connInfoUpstream[i][6].text.lstrip()
            power = power.replace(" dBmV","")
                
            perfdata += "'up_" + str(j) + "_pwr'=" + power + ";;;; "

        if args.verbose:
            verboseData += 'Upstream channels info'
            for i in upChannels:
                verboseData += i

    else:
        output = "CRITICAL - Connection issue"
        returnCode=2
else:
    output = "CRITICAL - Downstream channel unlocked"
    returnCode=2

output = "OK"
returnCode=0
if args.perfdata: output = output + '|' + perfdata

print(output)
if args.verbose: print(verboseData)
exit(returnCode)
