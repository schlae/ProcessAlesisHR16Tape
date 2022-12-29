# Read Alesis HR-16 Data Tapes
This simple and crappy Python program is designed to parse the contents of a WAV file containing the data recorded to a standard audio cassette by an Alesis HR-16 drum machine.

It's not complete and will not dump understandable or useful data, but it's probably a good starting point.

You don't need any special libraries, unless you want the histogram plot of the zero crossing interval, in which case you will need Numpy and PyPlot.

## Using the program
Just run `python ProcessTape.py wavefile.wav` to parse a given audio file. The program is hard coded to use files saved as uncompressed mono 16-bit signed sample data.

## Alesis HR-16 tape format
Here is what I know so far about the tape format.

There is a 1200Hz leader signal for several seconds.

A zero is encoded by a single cycle of a 1200Hz sine wave. A one is encoded by a single cycle of a 2400Hz sine wave.

In between data blocks, there is a gap of about 2.5ms. Data blocks are variable length. Each data block starts with approximately 32 zero bits followed by the sync word, which is 0101 0101 (0xAA).

The contents of the data blocks are not fully understood, but appear to be
| Offset | Length | Description |
|--------|--------|-------------|
| 0 | 1 | Block number. This appears to increment by one for each block. |
| 1 | 2 | Block length (little endian). It is short by 7 bytes. |
| 3 | 4 | Unknown header data. |
| 7 | n | Block data. |

## License
This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License. See [https://creativecommons.org/licenses/by-sa/4.0/](https://creativecommons.org/licenses/by-sa/4.0/).

