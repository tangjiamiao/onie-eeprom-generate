#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018年9月13号

@author: tjm
'''
import sys
import os

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

def getalltxtfilename2(path, typename): 
    txtfilenames=[] 
    for dirpath,dirnames,filenames in os.walk(path): 
        filenames=filter(lambda filename:filename[-3:]==typename,filenames) 
        filenames=map(lambda filename:os.path.join(dirpath,filename),filenames) 
        txtfilenames.extend(filenames)
        #print filenames
    return txtfilenames


if __name__ == '__main__':    
    arg = sys.argv[1:]
    if len(arg) < 1:
        usage();
        sys.exit(1)
    arg[0] = "as13_32h_f_rj_3_bmceeprom.bin"
    
    filenames=getalltxtfilename2("./", "bin")
    for filename in filenames:
        print "==========================================="
        print os.path.basename(filename)
        print "==========================================="
        
        decodeBinName(filename)
        print "\n\n"
        pass   

    #decodeBinName(arg[0])
