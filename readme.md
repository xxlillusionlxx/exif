# Basic EXIF data parser

This is a very basic EXIF data parser for jpeg files. This will go through the jpeg file and find all the markers, adding their location, size, and actual marker to their respective global arrays. These arrays are then printed out. While in the process of printing, the program checks to find the EXIF tag--when it does, it calls findIFD() and passes a subset of the data starting at the 0x4d mark to the function.


**How to run:** $>python3 exif.py [file name]
