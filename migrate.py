#!/bin/python3

####################################
# Xen Migration Performance Tester #
# Made by Ivar Slotboom aka f13rce #
# Made for Large Systems - OS3/SNE #
####################################

# Imports
import time
import os
import argparse
import subprocess

# Globals
resultsFileName = "results_{}.csv".format(time.asctime(time.localtime(time.time())).replace(" ", "_").replace(":", "."))
curlError = "curl: (7) Failed to connect to"

# Logging
def Log(aText):
	print("LOG [{}]: {}".format(time.asctime(time.localtime(time.time())), aText))

# Funcs
def GetTime():
	return int(round(time.time() * 1000))

def LogDowntime(aVMIP):
	WaitTillServerIsUp(aVMIP)
	WaitTillServerIsDown(aVMIP)
	startTime = GetTime()
	WaitTillServerIsUp(aVMIP)
	endTime = GetTime()
	delta = endTime - startTime

def PerformMigration(aHost, aTarget, aVMName, aVMIP, aIndex):
	# Preferably no logging in the migration process - it may affect the performance!

	# Ensuring our domain exists
	Log("Ensuring our domain exists by creating it...")
	os.system("sudo xl create /etc/xen/{}.cfg > /dev/null 2>&1".format(aVMName))

	# Destroy existing instance
	Log("Destroying previous instance so that XL has no issue with us transferring.")
	ssh = subprocess.Popen(["ssh", "-v", "root@{}".format(aTarget), "xl destroy {}".format(aVMName)],
		shell=False,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)
	Log("SSH xl destroy output: {}".format(ssh.stdout.readlines()))
	ssh.kill()

	# Start timer
	Log("Starting timer")
	startTime = GetTime()

	# Wait for termination
	#timeToSleep = 15
	#Log("Sleeping {} seconds so that the termination can peacefully continue...".format(timeToSleep))
	#time.sleep(timeToSleep)

	# Migrate
	Log("Performing migration")
	#os.system("sudo xl migrate {} root@{}".format(aVMName, aTarget))
	os.system("xl migrate -s \"ssh root@{} -i /root/.ssh/id_rsa\" {} \"\" --debug".format(aTarget, aVMName))

	# Stop timer
	# Check for uptime
	WaitTillServerIsUp(aVMIP)
	endTime = GetTime()

	# Store results
	Log("Done with the migration! Downtime was {}ms!".format(endTime - startTime))
	StoreResult(startTime, endTime, aHost, aTarget, aIndex)

def WaitTillServerIsUp(aVMIP):
	# Curl because the host is running apache2
	serverIsDown = True
	while serverIsDown:
		curlOutput = os.popen('curl {}'.format(aVMIP)).read()
		#Log("DEBUG: {}".format(curlOutput)) # COMMENT DISABLE THIS WHEN IT WORKS
		if not curlError in curlOutput:
			#Log("DEBUG: Server is up!") # COMMENT THIS WHEN IT WORKS
			serverIsDown = False
			break

def WaitTillServerIsDown(aVMIP):
	# Curl because the host is running apache2
	serverIsDown = False
	while serverIsDown:
		curlOutput = os.popen('curl {}'.format(aVMIP)).read()
		Log("DEBUG: Down check: {}".format(curlOutput)) # COMMENT DISABLE THIS WHEN IT WORKS
		if curlError in curlOutput:
			Log("DEBUG: Down check: Server is down!") # COMMENT THIS WHEN IT WORKS
			serverIsDown = True
			break


def StoreResult(aStartTime, aEndTime, aHost, aTarget, aIndex):
	with open(resultsFileName, "a") as f:
		f.write("{}, {}, {}, {}, {}, {}\n".format(aIndex, aEndTime - aStartTime, aStartTime, aEndTime, aHost, aTarget))

# Main
def main():
	# Parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-o", "--origin", help="IP address of the host machine that is performing the migration (e.g.: 145.100.104.48)")
	parser.add_argument("-t", "--target", help="IP address of the target machine that is receiving the migration (e.g.: 145.100.104.49)")
	parser.add_argument("-v", "--vmip", help="IP address of the VM that is running on the target machine (e.g.: 145.100.104.50)")
	parser.add_argument("-n", "--name", help="Name of the VM that is being migrated (e.g.: migration-cold)")
	parser.add_argument("-c", "--count", help="Amount of times the migration should be performed (e.g.: 32)")

	args = parser.parse_args()
	Log("Found args: {}".format((repr(args))))

	if args.origin == None or args.target == None or args.vmip == None or args.name == None or args.count == None:
		Log("Error: One or more required arguments are missing. Ask for --help for info.")
		return 1

	machineHost = args.origin
	machineTarget = args.target
	vmIP = args.vmip

	# Start with clean log file
	with open(resultsFileName, "w") as f:
		f.truncate()
		f.write("Test ID, Delta, Start time, End Time, Host, Target\n")

	# Ensure we have sudo rights
	Log("The migration command requires sudo - you may be prompted now to enter your password to grant sudo rights to prevent performance timing issues.")
	os.system("sudo echo \"Thank you - we now have sudo rights!\"")

	# Perform the migration
	Log("Will be performing {} migration tests.".format(args.count))
	for i in range(int(args.count)):
		Log("Performing migration \"{}\" {}-->{} (VM: {}) ({}/{})...".format(args.name, machineHost, machineTarget, vmIP, (i+1), args.count))
		PerformMigration(machineHost, machineTarget, args.name, vmIP, (i+1))
	Log("All done with the tests! Results have been saved to \"{}\"".format(resultsFileName))

	return 0

if __name__ == "__main__":
    main()
