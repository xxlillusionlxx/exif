#! user/bin/python3

import sys
import tags
import os
from struct import unpack

__author__ = 'jason'

class Exif:

    def __init__(self):
        self.fd = 0
        self._JPEG_HEADER = b'\xff\xd8'
        self._LAST_MARKER = b'\xff\xda'
        self._MRKBEGIN = '0xff'
        self._offset = 0 # used for holding current fd.seek() location for app markers
        self.marks = []
        self.size = []
        self.locations = []
        self._data = None
        self._found = False


    def open_file(self,file_name):
        try:
            print("Opening file: ", file_name)
            self.fd = open(file_name,'rb')
            self.verify(self.fd)

        except:
            print("File could not be found, please try again")
            sys.exit()

    def verify(self, fd):
        data = fd.read(2)
        if not data == self._JPEG_HEADER:
            print("Not a jpeg file. Exiting program...")
            sys.exit()
        else:
            print("Your JPEG opened successfully.")
            self._offset += 2 # now that we've confirmed it's a jpg, add 2 to set offset to location of 1st app marker

    '''
    # Finds all the markers, adding their location, size, and actual marker to
    # their respective global arrays.
    #
    # Then it prints these arrays out. While in the print loop, it checks to find
    # the EXIF tag--when it does, it calls findIFD() and passes a subset of the data
    # starting at the 0x4d mark to the function.
    #
    # Worth noting the data in this case is the data encompassed in the range from the
    # start of the IFD down to size of the IFD found.
    '''
    def markers(self):

        if not self.fd:
            print("Must open a file first before you can find markers.")

        self.fd.seek(self._offset) # move file pointer to position after ffd8
        self.locations.append(hex(self._offset))
        data = self.fd.read(2)

        while 1:
            if hex(data[0]) == self._MRKBEGIN:
                self.marks.append(self.convertToHex(data)) # append marker

                temp_marker = data

                data = self.fd.read(2) # read in next 2 bytes for size

                hexedSize = self.convertToHex(data)    # convert 2-byte size data into hex

                self.size.append(hexedSize)
                self._offset += int(hexedSize, 16) + 2
                self.fd.seek(self._offset)
                if temp_marker == self._LAST_MARKER:
                    break

            self.locations.append(hex(self._offset))
            data = self.fd.read(2)

            if not data:
                break

        count = 0

        for i in self.marks:
            print("[%6s]"%self.locations[count], " ", end='')
            print("Marker: ", self.marks[count], " ", end='')
            print("Size: ", self.size[count])

            self.fd.seek(int(self.locations[count], 16) + 4) # add 4 to skip over 2-byte app marker and 2-byte size
            self._data = self.fd.read(int(self.size[count], 16) - 2)

            if self._found == False:
                if self.isExif():
                    temp = self._data[6:]
                    self.findIFD(temp)
            else:
                temp = self._data[6:]
                self.findIFD(temp)
            count += 1

    def convertToHex(self, data):
        hex = '0x'
        for b in data:         # convert 2-byte size data into hex
            hex += "%02x" %b
        return hex

    def isExif(self):
        data = self._data[0:4]
        try:
            if bytes.decode(data) == 'Exif':
                self._found = True
                if bytes.decode(self._data[6:8]) != 'MM':
                    print("Little-endian detected. Exiting program")
                    sys.exit()

                else:
                    return True
            else:
                return False
        except:
            print("Decoding problem")

    def findIFD(self, data):

        bytes_per_component = [0,1,1,2,4,8,1,1,2,4,8,4,8]
        acceptable_formats = [1,2,3,4,5,7]

        temp = data[4:8] # get the long with the size; e.g 0008
        offset = int(self.convertToHex(temp), 16) # convert to int to get the size
        entries_numbers = int(self.convertToHex(data[offset:offset+2]), 16)
        print("%02sNumber of IFD entries: "%'', entries_numbers)

        i = 0
        while i < entries_numbers:
            tag_entry_loc = offset+ i*12 + 2
            format_loc = offset+ i*12 + 4
            components_loc = offset+ i*12 + 6
            data_loc = offset+ i*12 + 10

            tag_hex = self.convertToHex(data[tag_entry_loc:tag_entry_loc+2])
            tag = int(tag_hex, 16)
            format = int(self.convertToHex(data[format_loc: format_loc+2]), 16)
            components = int(self.convertToHex(data[components_loc: components_loc+4]), 16)
            entry_data = int(self.convertToHex(data[data_loc: data_loc+4]), 16)
            data_length = bytes_per_component[format]*components

            print("%02s"%'', tag_hex, " ", tags.TAGS[tag],": ", end='')

            if data_length <= 4:
                print(entry_data)
            else:
                if format in acceptable_formats:
                    print(bytes.decode(data[entry_data:entry_data+data_length]))

            #print(" Data Length: ", data_length)
            # print(" Component: ", components)
            # print(" Data: ", entry_data)
            i += 1



def usage():
    print("Usage: python3.2 exif.py <jpg file>")

def main():
  if len(sys.argv) != 2:
      usage()
  else:
      exf = Exif()
      exf.open_file(sys.argv[1])
      exf.markers()

if __name__=="__main__":
  main()