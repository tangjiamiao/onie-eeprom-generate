#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018年9月13号

@author: tjm
'''
import sys

from e2 import CommonArea
       
def usage():
    print("Usage: [platformfru.py eepromfilelocation]");
    print("       example: e2.py /sys/bus/i2c/device/2-0057");
        
    print("       use-default : ");
    print("                       0 : default");
    print("                       1 : change value");
    

def decodeBinName(filename):  
    retval = None  
    try:
        with open(filename, 'r') as fd:
            retval = fd.read()
    except Exception as e:
        print e
        return 
    fru = CommonArea()
    fru.initDefault()
    fru.decodeBin(retval) 
    pass

if __name__ == '__main__':    
    arg = sys.argv[1:]
    if len(arg) < 1:
        usage();
        sys.exit(1)
    arg[0] = "as13_48f8h_2_x86cpueeprom.bin"
    decodeBinName(arg[0])
