#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018年9月13号

@author: tjm
'''
import sys

from e2 import *
       
def usage():
    print("Usage: [platformfru.py eepromfilelocation]");
    print("       example: e2.py /sys/bus/i2c/device/2-0057");
        
    print("       use-default : ");
    print("                       0 : default");
    print("                       1 : change value");
    
def printbinvalue(b):
    index = 0
    print "     ",
    for width in range(16):
        print "%02x " % width,
    print ""
    for i in range(0, len(b)):
        if index % 16 == 0:
            print " "
            print " %02x  " % i ,
        print "%02x " % ord(b[i]),
        index += 1
    print ""  

def decodeBinName(filename):  
    retval = None  
    with open(filename, 'r') as fd:
        retval = fd.read()
    fru = CommonArea()
    fru.initDefault()
    fru.decodeBin(retval) 
    pass

if __name__ == '__main__':    
    arg = sys.argv[1:]
    if len(arg) < 1:
        usage();
        sys.exit(1)
    arg[0] = "xeon_d_c_2_x86cpueeprom.bin"
    decodeBinName(arg[0])
