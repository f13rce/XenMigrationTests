#!/bin/python3

import sys

high = 0
low = 9999999999
average = 0
median = 0
deltas = []
total = 0

with open("{}".format(sys.argv[1]), "r") as f:
	f.readline() # Skip headers
	i = 0
	while True:
		try:
			i += 1
			# Fetch delta
			line = f.readline()
			values = line.split(", ")
			delta = int(values[1])

			# Process delta
			deltas.append(delta)
			average += delta
			if delta > high:
				high = delta
			if delta < low:
				low = delta
			total += delta
		except:
			break

# Get avg/median
average /= i
average = int(round(average))

median = deltas[round(i / 2)]

# Log in OS3-wiki format
print("^Type^Value (ms)^")
print("|Total tests|{}|".format(i))
print("|High|{}|".format(high))
print("|Low|{}|".format(low))
print("|Mean|{}|".format(average))
print("|Median|{}|".format(median))
print("|Total|{}|".format(total))
