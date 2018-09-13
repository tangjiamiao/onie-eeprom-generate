#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018�?�?�?
@author: tjm
'''

from bitarray import bitarray
from datetime import datetime

SUGGESTED_SIZE_COMMON_HEADER = 8
SUGGESTED_SIZE_INTERNAL_USE_AREA = 72
SUGGESTED_SIZE_CHASSIS_INFO_AREA = 32
SUGGESTED_SIZE_BOARD_INFO_AREA = 64
SUGGESTED_SIZE_PRODUCT_INFO_AREA = 80


SUGGESTED_SIZE_INTERNAL_USE_AREA_TYPE = 1
SUGGESTED_SIZE_CHASSIS_INFO_AREA_TYPE = 2
SUGGESTED_SIZE_BOARD_INFO_AREA_TYPE = 3
SUGGESTED_SIZE_PRODUCT_INFO_AREA_TYPE = 4
SUGGESTED_SIZE_MULTI_RECORD_AREA_TYPE = 5

INITVALUE = b'\x00'
resultvalue = INITVALUE * 256
COMMON_HEAD_VERSION = b'\x01'

__DEBUG__ = "N"
def e_print(err):
    print("ERROR: " + err)

def d_print(debug_info):
    if(__DEBUG__ == "Y"):
        print(debug_info)

def p_print(prompt):
    print("PROMPT: " + prompt)

class BaseArea():
    __childList = None
    def __init__(self, name="", size = 0, offset = 0):
        self.__childList = []
        self._offset = offset
        self.name = name
        self._size = size
        self._isPresent = False 
        self._data = b'\x00' * size
        self.__dataoffset = 0                  
    
    def addChild(self, arrlist):
        self.childList.append(arrlist)
        arrlist.offset = self.__dataoffset + arrlist.size
        self.data = self.data[0 : self.__dataoffset + arrlist.size - 1] + arrlist.data + self.data[self.__dataoffset + arrlist.size : self.size]        
        self.__dataoffset += arrlist.size  
        printbinvalue(self.data)
        
    def reload(self):        
        tempdata = ""
        for it in self.childList:       
            tempdata += it.data
        self.data = tempdata
        
    @property
    def childList(self):
        return self.__childList;  
                    
    @property
    def offset(self):
        return self._offset;    
    
    @property
    def size(self):
        return self._size; 
     
    @property
    def data(self):
        return self._data;  
    @property
    def isPresent(self):
        return self._isPresent;    
    
class InternalUseArea(BaseArea):
    pass
class ChassisInfoArea(BaseArea):
    pass


def getTypeLength(value):        
        a = bitarray(8)
        a.setall(False)
        a[0:1] =1
        a[1:2] =1
        x = ord(a.tobytes())
        return  x | len(value)  
    
class BoardInfoArea(BaseArea):        
    def recalcute(self):
        d_print("BoardInfoArea version:%x" % ord(self.boardversion))
        d_print("BoardInfoArea length:%d" % self.size)
        d_print("BoardInfoArea language:%x" % self.language)   
        d_print("BoardInfoArea mfg_date:%x" % self.mfg_date)        
        
        self.data = chr(ord(self.boardversion)) + chr(self.size/8) + chr(self.language)
        
        self.data += chr(self.mfg_date & 0xFF)
        self.data += chr((self.mfg_date >> 8 ) & 0xFF)
        self.data += chr((self.mfg_date >> 16 ) & 0xFF)
                
        d_print("BoardInfoArea boardManufacturer:%s" % self.boardManufacturer)   
        typelength = getTypeLength(self.boardManufacturer);
        self.data += chr(typelength)
        self.data += self.boardManufacturer
        
        self.data += chr(getTypeLength(self.boradProductName))
        self.data += self.boradProductName
        
        self.data += chr(getTypeLength(self.boardSerialNumber))
        self.data += self.boardSerialNumber
        
        self.data += chr(getTypeLength(self.boardPartNumber))
        self.data += self.boardPartNumber  
           
        self.data += chr(getTypeLength(self.FRUFileID))
        self.data += self.FRUFileID    
                
        self.data += chr(0xc1);
        d_print( "self.data:%d"% len(self.data))        
        d_print( "self.size:%d" % self.size )
                         
        for tianchong in range(self.size -len(self.data) -1):
            self.data += INITVALUE
            
        test = 0
        for index in range(len(self.data)):
            test += ord(self.data[index])    
        
        #checksum
        checksum = 0x100 - (test % 256)
        d_print("board info checksum:%x" % checksum)               
        self.data += chr(checksum)
    def getMfgDate(self):            
        starttime = datetime(1996,1,1,0,0,0)
        endtime = datetime.now()
        seconds =  (endtime - starttime).total_seconds()
        mins = seconds / 60
        m = int(round(mins))                
        return m
        
    @property
    def language(self):        
        self._language = 25;  
        return self._language;   
            
    @property
    def mfg_date(self):       
        self._mfg_date = self.getMfgDate();
        return self._mfg_date;            
    
    @property
    def boardversion (self):
        self._boardversion = COMMON_HEAD_VERSION;
        return self._boardversion; 
    @property
    def FRUFileID (self):
        return self._FRUFileID; 
    @property
    def boardPartNumber(self):
        return self._boardPartNumber; 
    @property
    def boardSerialNumber(self):
        return self._boardSerialNumber;  
    @property
    def boradProductName(self):
        return self._boradProductName;  
    @property
    def boardManufacturer(self):
        return self._boardManufacturer;    
    @property
    def boardTime(self):
        return self._boardTime;  
    @property
    def fields(self):
        return self._fields; 
       
class ProductInfoArea(BaseArea):
    @property
    def productVersion (self):
        self._productVersion = COMMON_HEAD_VERSION;
        return self._productVersion; 
    @property
    def language(self):        
        self._language = 25;  
        return self._language;
    @property
    def productManufacturer(self):
        return self._productManufacturer;  
    @property
    def productName(self):
        return self._productName;  
    @property
    def productPartModelName(self):
        return self._productPartModelName; 
    @property
    def productSerialNumber(self):
        return self._productSerialNumber;  
    @property
    def productAssetTag(self):
        return self._productAssetTag;  
    @property
    def FRUFileID(self):
        return self._FRUFileID;  
    
class MultiRecordArea(BaseArea):
    pass

class Field():    
    def __init__(self, fieldType = "ASCII", fieldData = ""):
        self.fieldData  = fieldData
        self.fieldType  = fieldType        
    @property
    def data(self):
        return self._data; 
    @property
    def fieldType(self):
        return self._fieldType; 
    @property
    def fieldData(self):
        return self._fieldData; 

class CommonArea(BaseArea):
    def initDefault(self):
        self.version = COMMON_HEAD_VERSION 
        self.internalUserAreaOffset = INITVALUE
        self.chassicInfoAreaOffset = INITVALUE
        self.boardInfoAreaOffset = INITVALUE
        self.productinfoAreaOffset = INITVALUE
        self.multiRecordAreaOffset = INITVALUE
        self.PAD = INITVALUE
        self.zeroCheckSum = INITVALUE
        self.offset = SUGGESTED_SIZE_COMMON_HEADER
        
        internaluserarea = InternalUseArea(name="Internal Use Area", size= SUGGESTED_SIZE_INTERNAL_USE_AREA)     
        chassinfoarea = ChassisInfoArea(name="Chassis Info Area", size= SUGGESTED_SIZE_CHASSIS_INFO_AREA)
        boardinfoarea = BoardInfoArea(name="Board Info Area", size= SUGGESTED_SIZE_BOARD_INFO_AREA)     
        productInfoArea = ProductInfoArea(name="Product Info Area ", size= SUGGESTED_SIZE_PRODUCT_INFO_AREA)   
        multiRecordArea = MultiRecordArea(name="Product Info Area ")    
        self.ProductInfoArea = productInfoArea
        self.InternalUseArea = internaluserarea
        self.BoardInfoArea = boardinfoarea
        self.ChassisInfoArea = chassinfoarea  
        self.MultiRecordArea = multiRecordArea        
        self.recalcute()
     
    @property
    def version(self):
        return self._version; 
                
    @property
    def internalUserAreaOffset(self):        
        return self._internalUserAreaOffset; 
    @property
    def chassicInfoAreaOffset(self):
        return self._chassicInfoAreaOffset; 
        
    @property
    def productinfoAreaOffset(self):
        return self._productinfoAreaOffset; 
    @property
    def boardInfoAreaOffset(self):
        return self._boardInfoAreaOffset; 
    @property
    def multiRecordAreaOffset(self):
        return self._multiRecordAreaOffset; 
    @property
    def PAD(self):
        return self._PAD; 
    @property
    def zeroCheckSum(self):
        return self._zeroCheckSum;
    
    @property
    def ProductInfoArea(self):
        return self._ProductInfoArea; 
    
    @property
    def InternalUseArea(self):
        return self._InternalUseArea;    
    @property
    def BoardInfoArea(self):
        return self._BoardInfoArea; 
    @property
    def ChassisInfoArea(self):
        return self._ChassisInfoArea; 
    @property
    def MultiRecordArea(self):
        return self._multiRecordArea; 
    @property
    def bindata(self):
        return self._bindata;  
    
    def recalcuteCommonHead(self):
        self.offset = SUGGESTED_SIZE_COMMON_HEADER
        d_print("before %d" % self.offset)
        if self.InternalUseArea.isPresent:            
            self.internalUserAreaOffset = self.offset/8
            self.offset += SUGGESTED_SIZE_INTERNAL_USE_AREA   
            d_print("InternalUseArea is present offset:%d" % self.offset)            
        if self.ChassisInfoArea.isPresent:
            self.chassicInfoAreaOffset = self.offset/8
            self.offset += SUGGESTED_SIZE_CHASSIS_INFO_AREA 
            d_print("ChassisInfoArea is present offset:%d" % self.offset) 
        if self.BoardInfoArea.isPresent:
            self.boardInfoAreaOffset = self.offset/8
            self.offset += SUGGESTED_SIZE_BOARD_INFO_AREA
            d_print("BoardInfoArea is present offset:%d" % self.offset) 
        if self.ProductInfoArea.isPresent:          
            self.productinfoAreaOffset = self.offset/8
            self.offset += SUGGESTED_SIZE_PRODUCT_INFO_AREA  
            d_print("ProductInfoArea is present offset:%d" % self.offset) 
        if self.MultiRecordArea.isPresent:
            self.multiRecordAreaOffset = self.offset/8
            d_print("MultiRecordArea is present offset:%d" % self.offset) 
        
        if self.internalUserAreaOffset == INITVALUE:
            self.internalUserAreaOffset = 0
        if self.productinfoAreaOffset == INITVALUE :
            self.productinfoAreaOffset = 0
        if self.chassicInfoAreaOffset  == INITVALUE:
            self.chassicInfoAreaOffset = 0            
        if self.boardInfoAreaOffset  == INITVALUE:
            self.boardInfoAreaOffset = 0
        if self.multiRecordAreaOffset  == INITVALUE:
            self.multiRecordAreaOffset = 0
        self.zeroCheckSum = 0x100 - ord(self.version) - self.internalUserAreaOffset -self.chassicInfoAreaOffset -self.productinfoAreaOffset \
                            - self.boardInfoAreaOffset -self.multiRecordAreaOffset
        d_print("zerochecksum:%x" % self.zeroCheckSum)        
        self.data = self.version + chr(self.internalUserAreaOffset) + chr(self.chassicInfoAreaOffset) + chr(self.boardInfoAreaOffset) + chr(self.productinfoAreaOffset) + chr(self.multiRecordAreaOffset) + self.PAD + chr(self.zeroCheckSum);
            
        
    def recalcutebin(self):
        self.bindata = ""        
        self.bindata += self.data                            
        if self.InternalUseArea.isPresent:
            d_print("InternalUseArea is present")
            self.bindata += self.InternalUseArea.data  
        if self.ChassisInfoArea.isPresent:
            d_print("ChassisInfoArea is present")
            self.bindata += self.ChassisInfoArea.data  
        if self.BoardInfoArea.isPresent:
            d_print("BoardInfoArea is present")
            self.BoardInfoArea.recalcute()
            self.bindata += self.BoardInfoArea.data  
        if self.ProductInfoArea.isPresent:
            d_print("ProductInfoArea is present")
            self.bindata += self.ProductInfoArea.data  
        if self.MultiRecordArea.isPresent:
            d_print("MultiRecordArea is present")
            self.bindata += self.ProductInfoArea.data          
        totallen = len(self.bindata)
        if (totallen < 256):
            for left_t in range(0, 256 - totallen):
                self.bindata += chr(0x00)                  
    def recalcute(self):
        self.recalcuteCommonHead()
        self.recalcutebin() 
        
def printbinvalue(b):
    index = 0
    for i in range(0, len(b)):
        if index % 16 == 0:
            print " "
        print "%02x "% ord(b[i]),
        index += 1
    print ""       
    
def initEERPOMTree():    
    fru = CommonArea()
    fru.initDefault()
    boardinfoarea = BoardInfoArea(name="Board Info Area", size= SUGGESTED_SIZE_BOARD_INFO_AREA)  
    boardinfoarea.isPresent = True
    
    boardinfoarea.boardManufacturer = "tjm"
    boardinfoarea.boradProductName = "tjm"
    boardinfoarea.boardSerialNumber= "0000000000000"
    boardinfoarea.boardPartNumber= "tjm-100"
    boardinfoarea.FRUFileID= "md5sum"
              
    fru.BoardInfoArea = boardinfoarea
    #fru.ProductInfoArea.isPresent = True
    #fru.MultiRecordArea.isPresent = True    
    fru.recalcute()    
    printbinvalue(fru.bindata) 
    write_bin_file("test_ali.bin", fru.bindata)       

def write_bin_file(filename, _value):
    retname = filename 
    filep = open(retname, 'wb')
    for x in _value:
        filep.write(str(x))
    filep.close();

def main():
    initEERPOMTree()

if __name__ == '__main__':
    main()
    pass