#!/usr/bin/env python3

# Nagios-compliant plugin to check the connectivity status on a 
# VOO (Belgian ISP) Technicolor modem.
# Written by Eric Viseur <eric.viseur@gmail.com>, 2021
# Released under MIT license

import mechanize
import array
import argparse
import yaml
import os
from lxml import etree


# ---- constants --------------------------------------------------------------

HOST_ADDRESS = '192.168.100.1'
CONFIG_FILE = 'check_voo.yml'

# ---- parse the arguments ----------------------------------------------------

def create_args():
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      description = 'Nagios-compliant plugin to check the connectivity status on a VOO Technicolor modem in bridge mode',
      epilog = "When not using Vault, the configuration file is expected to present the following contents:\n\nlogin: <your Voo modem login>\npassword: <your Voo modem password>\n\n\nIf using Vault:\n\nserver: <Vault server URL>\nrole: <AppRole role-id>\nsecret: <AppRole secret-id>\nmountpoint: <The mount point of the target KV v2 engine>\npath: <The path inside the mountpoint that contains the modem credentials>\n\nRefer to README.md in https://github.com/sephiroth1395/nagios-plugins for more info on Vault usage.\n",
      )

  parser.add_argument("-H", "--host", action = "store",
    dest = 'modemAddress', default = HOST_ADDRESS,
    help = ("IP address of the VOO modem. Default [%s]" % HOST_ADDRESS))

  parser.add_argument("-c", "--config-file", action = "store",
    dest = 'configFile', default = CONFIG_FILE,
    help = ("Configuration file location Default [%s]" % CONFIG_FILE))

  parser.add_argument("--perfdata", action = 'store_true',
    help = 'Append perfdata to the plugin output.')

  parser.add_argument("-v", "--verbose", action = 'store_true',
    help = 'Produce verbose output.')

  parser.add_argument("-V", '--use-vault', action = 'store_true',
    dest = 'useVault', help = 'Get the modem credentials from HashiCorp Vault.')

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

# ---- get the modem credentials from Vault -----------------------------------

def get_creds_from_vault(configFile):

  # Check if the config file exists
  if os.path.exists(configFile):
    # Attempt to read the config file contents
    try:
      stream = open(configFile, 'r')
      settings = yaml.load(stream, Loader=yaml.BaseLoader)
      vaultServer = settings['server']
      vaultRole = settings['role']
      vaultSecret = settings['secret']
      vaultMountPoint = settings['mountpoint']
      vaultPath = settings['path']
    except:
      print("CRITICAL - Error reading the configuration file %s" % configFile)
      exit(2)
  else:
    print("CRITICAL - Configuration file %s does not exist" % configFile)
    exit(2)

  # Open a connection to the Vault server
  try:
    vault = hvac.Client(url=vaultServer)
    vault.auth.approle.login(
      role_id=vaultRole,
      secret_id=vaultSecret,
    )
  except:
    print("CRITICAL - Error connecting to Vault server %s" % vaultServer)
    exit(2)
  
  # Get the modem credentials from the provided path
  try:
    vaultData = vault.secrets.kv.v2.read_secret_version(path=vaultPath, mount_point=vaultMountPoint)
    vooLogin = vaultData['data']['data']['login']
    vooPassword = vaultData['data']['data']['password']
    return(vooLogin, vooPassword)
  except:
    print("CRITICAL - Error getting the modem credentials from the KV path %s/%s" % (vaultMountPoint,vaultPath))
    exit(2)


# ---- main routine -----------------------------------------------------------
# ---- This plugin leverages the mechanize python module to mimic the      ----
# ---- behaviour of a human user.  Sorry for the messy code but the        ----
# ---- WebUI HTML output is a mess in itself                               ----
# -----------------------------------------------------------------------------

args = create_args()

# Depending on whether or not Vault is required to be used, the credentials
# are fetched differently
if args.useVault:
  import hvac
  (vooLogin, vooPassword) = get_creds_from_vault(args.configFile)
else:
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
    br.open('http://' + args.modemAddress + '/RgConnect.asp')
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
	# Populate arrays with the properties of each channel
        downChannels = []
        upChannels = []

        # Starting with Element 2, connInfoDownstream contains each downstream channel
        for i in range(2, 18):
            j = i-1
            modulation = connInfoDownstream[i][2].text
            baudrate = connInfoDownstream[i][4].text
            power = connInfoDownstream[i][6].text.lstrip()
            power = power.replace(" dBmV","")
            snr = connInfoDownstream[i][7].text.lstrip()
            snr = snr.replace(" dB","")
            
            downChannels.append([modulation, baudrate, power, snr])
            perfdata += "'down_" + str(j) + "_pwr'=" + power + ";;;; 'down_" + str(j) + "_snr'=" + snr + ";;;; "

        # Starting with Element 2, connInfoUpstream contains each downstream channel
        for i in range(2, 6):
            j = i-1
            modulation = connInfoUpstream[i][2].text
            baudrate = connInfoUpstream[i][4].text
            power = connInfoUpstream[i][6].text.lstrip()
            power = power.replace(" dBmV","")
            
            upChannels.append([modulation, baudrate, power])
            perfdata += "'up_" + str(j) + "_pwr'=" + power + ";;;; "

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

if args.verbose:
  print("\nDownstream channels")
  for i in downChannels:
    print("\t%s" % i)
  print("\nUpstream channels")
  for i in upChannels:
    print("\t%s" % i)

exit(returnCode)

