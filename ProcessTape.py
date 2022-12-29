''' Parse audio cassette data contained in wave files.

Copyright (C) 2022 Tube Time.

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
Commons, PO Box 1866, Mountain View, CA 94042, USA.

'''

import struct
import sys
import numpy as np
from matplotlib import pyplot as plt

if len(sys.argv) != 2:
    print("Usage: ProcessTape.py filename")
    quit()

# Read the input file
f = open(sys.argv[1], "rb")
d = f.read()
f.close()

# Turn it into an array of samples
# Let's not bother parsing the header.
# Just assume it is 16-bit signed samples.
p = struct.unpack("<" + str(int((len(d)) / 2)) + "h", d)[22:]

# Now look for zero crossings in the sample data
curdat = 0
curdat_prev = 0
oldcrossing = 0
crossings = []
THRESHOLD = 4000        # Threshold so we don't pick up on noise during silence
for i in range(len(p)):
    s = p[i]
    # threshold with hysteresis
    if (curdat == 0) and (s > THRESHOLD):
        curdat = 1
    if (curdat == 1) and (s < -THRESHOLD):
        curdat = 0

    # zero crossing
    if (curdat != curdat_prev):
        curdat_prev = curdat
        pulsewidth = i - oldcrossing
        oldcrossing = i
        if (pulsewidth < 100):
            crossings.append(pulsewidth)

# Optionally plot the histogram of the zero crossing periods
if 0:
    plt.hist(crossings, bins=100)
    plt.show()

# The next stage is to turn the zero crossings into bits.
# This is precalculated out so 1200=0 and 2400=1.
# Remember that a single cycle (of 1200hz or 2400hz) is actually two zero
# crossings.
bstream = []
prevc = 0
previ = 0
for i in range(len(crossings)):
    c = crossings[i]
    # 1200Hz
    if (c > 15) and (c < 25):
        bstream.append(0)
    # 2400Hz
    if (c < 15) and (c > 5):
        bstream.append(1)
    if (c > 25):
        bstream.append(c)
#        if (c > 70):
#            print(i-previ)
#            previ = i
    prevc = c

# Quick and dirty function to pretty print a block of data in hex
def pblock(block):
    l = len(block)
    wi = 16
    rl = l % wi
    for i in range(0, wi * int(l / wi), wi):
        print(' '.join(['%02x' % a for a in block[i:i+wi]]))
    if rl != 0:
        print(' '.join(['%02x' % a for a in block[-rl:]]))

# Quick and dirty function to print any strings in a block of data
def pblock2(block):
    st = ""
    for c in block:
        if (c > 31) and (c < 127):
            st += chr(c)
    print(st)

# This is our sync signal: A long string of 20 zeros followed by 10101010.
# The bits are doubled up because a sine wave has two zero crossings.
syncbits = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0]

# Now go through the whole stream of zero crossings
synced = False
i = 32
bcount = 0
lasti = 32
while (i < len(bstream)):
    # Can we find sync at this offset, looking back?
    if syncbits == bstream[i-len(syncbits):i]:
        # Yes, so set things up to read data.
        start = i
        bitcount = 0
        cbyte = 0
        synced = True
        print ("Sync at ", start)
        block = []
        # Debug, just print raw data
        if 0:
            print(bstream[i:i+1000])
            quit()
    # If we're synced, clock in the data
    if synced:
        # 11 or 00 means we have a 1 or a 0 (two zero crossings needed)
        # and anything else means we lost synchronization
        if bstream[i] == bstream[i+1]:
            # Clock the data in LSB first. Other tape formats might go
            # MSB first, so this is where you change that.
            if bstream[i] == 1 and bstream[i+1] == 1:
                cbyte = (cbyte >> 1) | 0x80
            elif bstream[i] == 0 and bstream[i+1] == 0:
                cbyte = (cbyte >> 1)
            # Advanced one additional zero cross (we are going two at a
            # time when in sync)
            bitcount += 1
            i += 1
            # If we have 8 bits of data, place this byte in our data block.
            if bitcount == 8:
                bitcount = 0
                block.append(cbyte)
                cbyte = 0
        else:
            print ("Loss of sync (diff=", i-lasti)
            lasti = i
            synced = False
            # Print out previously decoded block
            print ("Block length:", len(block), hex(len(block)))
            print ("Block #", bcount)
            pblock(block)
            # Optionally, print the strings in the block
            if 0:
                pblock2(block)
            bcount += 1
            # Optionally, we can stop after a certain block count
            # if we don't want to parse the whole recording
            if 0:
                if bcount == 2:
                    break
    # Go to the next zero crossing
    i += 1

# All done.

