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

def PerformMigration(aHost, aTarget, aVMName, aVMIP):
	# Preferably no logging in the migration process - it may affect the performance!
	# Start timer
	WaitTillServerIsUp() # First confirm the server is up
	startTime = GetTime()

	# Migrate
	os.system("sudo xl migrate {} root@{}".format(aVMName, aTarget))

	# Check for uptime
	WaitTillServerIsUp()

	# Stop timer
	endTime = GetTime()

	# Store results
	Log("Done with the migration in {}ms!".format(endTime - startTime))
	StoreResult(startTime, endTime, aHost, aTarget)

def WaitTillServerIsUp():
	# Curl because the host is running apache2
	serverIsDown = True
	while serverIsDown:
		curlOutput = os.popen('curl {}'.format(aVMIP)).read()
		Log("DEBUG: {}".format(curlOutput)) # COMMENT DISABLE THIS WHEN IT WORKS
		if not curlError in curlOutput:
			Log("DEBUG: Server is up!") # COMMENT THIS WHEN IT WORKS
			serverIsDown = False
			break


def StoreResult(aStartTime, aEndTime, aHost, aTarget):
	with open(resultsFileName, "a") as f:
		f.write("{}, {}, {}, {}, {}\n".format(aEndTime - aStartTime, aStartTime, aEndTime, aHost, aTarget))

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
		f.write("Delta, Start time, End Time, Host, Target\n")

	# Ensure we have sudo rights
	Log("The migration command required sudo - you may be prompted now to enter your password to grant sudo rights to prevent performance timing issues.")
	os.system("sudo echo \"Thank you - we now have sudo rights!\"")

	# Perform the migration
	Log("Will be performing {} migration tests.".format(args.count))
	for i in range(int(args.count)):
		Log("Performing migration \"{}\" {}-->{} (VM: {}) ({}/{})...".format(args.name, machineHost, machineTarget, vmIP, i, args.count))
		PerformMigration(machineHost, machineTarget, args.name, vmIP)

	return 0

if __name__ == "__main__":
    main()
