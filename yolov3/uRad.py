import struct
import sys
import math
import matplotlib.pyplot as plt
import numpy as np
import csv

global csv_file
global make_plot

def tlvHeaderDecode(data):
    print("Length of data:", len(data))
    tlvType, tlvLength = struct.unpack('2I', data)
    return tlvType, tlvLength

def parseRangeProfile(data, tlvLength):
    looper = int(tlvLength / 2)
    a = np.ones((256,1))
    for i in range(looper):
        rangeProfile = struct.unpack('H', data[2*i:2*i+2])
        a[i] = (rangeProfile[0] * 1.0 * 6.0 / 8.0  / (1 << 8))*10.0
        #a[i] = rangeProfile[0]
        #print("\tRangeProf[%0.3fm]:\t%07.3fdB "%(i * 0.044, 20 * math.log10(2**(rangeProfile[0]/(2**9))))) #0.1249921875 is based on profile confg
        #print("\tTLVType:\t%d "%(2))


    with open(csv_file, 'ab') as f:
        writer = csv.writer(f, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        a.tofile(f, sep=',',format='%10.5f')
        writer.writerow('')

    if make_plot == True:
        plt.clf()
        plt.plot(a)
        plt.ylabel('Range Profile Zero')
        plt.draw()
        plt.pause(0.02)



def tlvHeader(data, skip_range=False, skip_stats=False):
    pendingBytes = 29
    headerLength = 28
    a= 1
    while(data):
        a=2
        magic = b'\x02\x01\x04\x03\x06\x05\x08\x07'
        offset = data.find(magic)
        data = data[offset:]
        data = data[8:]
        try:
            version, length, platform, frameNum, cpuCycles, numObj, numTLVs = struct.unpack('<7I', data[:headerLength])
        except struct.error as e:
            #print "Improper TLV structure found: ", (data,)
            print("Error ", e)
            print(pendingBytes)
            break

        print("Packet ID:\t%d "%(frameNum))
        print("Version:\t%x "%(version))
        print("TLV:\t\t%d "%(numTLVs))
        print("Detect Obj:\t%d "%(numObj))
        print("Platform:\t%X"%(platform))
        #print("Subframe:\t%d "%(subFrameNum))
        print("")

        pendingBytes = length - headerLength
        data = data[headerLength+4:]

        counter = 0
        n= 1 # number of TLVs
        for i in range(n):
            tlvType, tlvLength = tlvHeaderDecode(data[:8])

            data = data[8:]

            if (tlvType == 3):
               # parseDetectedObjects(data, tlvLength)
               b = 2 # I have focused on range profile
            elif (tlvType == 2):
                if not skip_range:
                    parseRangeProfile(data, tlvLength)
                    b=2
            elif (tlvType == 6):
                if not skip_stats:
                    #parseStats(data, tlvLength)
                    b=2 # I have focused on range profile
                #tlvLength = tlvLength + 4
                b=2
            else:
                #print("Unidentified tlv type %d"%(tlvType))
                b=2

            #as some corrupted frames ruin the plot, I am incremeting manually
            if counter == 0:
                data = data[512:]
            elif counter == 1:
                data = data[512:]
            elif counter == 2:
                data = data[24:]
            counter += 1
            #data = data[tlvLength:]
            pendingBytes -= (8+tlvLength)




if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: parseTLV.py inputFile.bin plot/no_plot")
        sys.exit()

    fileName = sys.argv[1]
    csv_file = fileName + ".csv"
    rawDataFile = open(fileName, "rb")
    rawData = rawDataFile.read()
    rawDataFile.close()

    if len(sys.argv) == 3:
        if sys.argv[2] == "no_plot":
            make_plot = False
            print("plot False")
        else:
            make_plot = True
            print("plot True")
    else:
        make_plot = True
        print("ploe true")

    print ("make_plot %d" % make_plot)


    tlvHeader(rawData, skip_stats=True, skip_range=False)