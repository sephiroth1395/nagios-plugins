#!/usr/bin/env python3

# Nagios-compliant plugin to check results of the last Puppet agent run.
# This plugin is heavily inspired on Roland Wolters' plugin release in 2013 and
# can be seen as a Python 3 rewrite, although the structure slightly differs
# due to personal preference.
# Written by Eric Viseur <eric.viseur@gmail.com>, 2021
# Released under MIT license

import argparse
import yaml
import os
import datetime

# ---- constants --------------------------------------------------------------

PUPPET_LAST_RUN_FILE = '/opt/puppetlabs/puppet/public/last_run_summary.yaml'
WARNING_THRESHOLD = 1200
CRITICAL_THRESHOLD = 2700
EXIT_STATUS = ['OK', 'WARNING', 'CRITICAL']

# ---- parse the arguments ----------------------------------------------------

def create_args():
  parser = argparse.ArgumentParser(
      description = 'Nagios-compliant plugin to check results of the last Puppet agent run',
      )

  parser.add_argument("-F", "--file", action = "store",
    dest = 'puppetLastRunFile', default = PUPPET_LAST_RUN_FILE,
    help = ("Location of the last_run_summary.yaml file. Default [%s]" % PUPPET_LAST_RUN_FILE))

  parser.add_argument("-w", "--warn", action = "store", type = int,
    dest = 'warningThreshold', default = WARNING_THRESHOLD,
    help = ("Seconds since the last Puppet run to trigger a Warning alert. Default [%i]" % WARNING_THRESHOLD))

  parser.add_argument("-c", "--crit", action = "store", type = int,
    dest = 'criticalThreshold', default = CRITICAL_THRESHOLD,
    help = ("Seconds since the last Puppet run to trigger a Critical alert. Default [%i]" % CRITICAL_THRESHOLD))

  args = parser.parse_args()
  return args

# ---- output the status and exit ---------------------------------------------
def end_script(code, message):
  print("%s - %s" % (EXIT_STATUS[code], message))
  exit(code)


# ---- convert secinds into a human readable time span ------------------------

def secsToReadableString(secs):
    
    days = secs // 86400
    hours = (secs % 86400) // 3600
    minutes = (secs % 3600) // 60
    seconds = secs % 60
    message = '%d seconds ago' % seconds
    if minutes:
        message = '%d minutes and %s' % (minutes, message)
    if hours:
        message = '%d hours, %s' % (hours, message)
    if days:
        message = '%d days, %s' % (days, message)
    return message


# ---- mainline ---------------------------------------------------------------

# Process the arguments
args = create_args()

# Check if the Puppet status file can be read
if not os.path.isfile(args.puppetLastRunFile):
  end_script(2, ("Cannot open %s.  Check permissions and Puppet status." % args.puppetLastRunFile))

# Load the Puppet status file into a dictionnary
try:
  stream = open(args.puppetLastRunFile, 'r')
  puppetStatus = yaml.load(stream, Loader=yaml.BaseLoader)
except:
  end_script(2, 'Error parsing the Puppet status file')

# Check if any resource is in failed state
if int(puppetStatus['resources']['failed']) > 0:
    end_script(2, ("%s resource failures" % puppetStatus['resources']['failed']))

# Check if any event failure occured
if int(puppetStatus['events']['failure']) > 0:
    end_script(2, ("%s event failures" % puppetStatus['events']['failure']))

# Check last run age versus the defined thresholds
currentTime = datetime.datetime.now()
lastRunTime = datetime.datetime.fromtimestamp(int(puppetStatus['time']['last_run']))
timeDelta = currentTime - lastRunTime

timeDiff = timeDelta.total_seconds()
lastPuppetRun = secsToReadableString(timeDiff)

if lastRunTime > currentTime:
  end_script(2, 'Puppet summary file modified in the future!')
elif timeDiff > args.criticalThreshold: returnCode = 2
elif timeDiff > args.warningThreshold:  returnCode = 1
else: returnCode = 0

end_script(returnCode, ("Puppet last ran %s" % lastPuppetRun))
