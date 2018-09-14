#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018年9月
@author: tjm
'''

from bitarray import bitarray
from datetime import datetime, timedelta
import requests
import ConfigParser
import sys

SUGGESTED_SIZE_COMMON_HEADER = 8
SUGGESTED_SIZE_INTERNAL_USE_AREA = 72
SUGGESTED_SIZE_CHASSIS_INFO_AREA = 32
SUGGESTED_SIZE_BOARD_INFO_AREA = 64
SUGGESTED_SIZE_PRODUCT_INFO_AREA = 80

INITVALUE = b'\x00'
resultvalue = INITVALUE * 256
COMMON_HEAD_VERSION = b'\x01'
CONFIG_FILE = "product.conf"
    
BOARDINFOAREAISPRESETN = 'boardinfoarea.ispresent'
BOARDINFOAREABOARDMANUFACTURER = 'boardinfoarea.boardmanufacturer'
BOARDINFOAREABORADPRODUCTNAME = 'boardinfoarea.boradproductname'
BOARDINFOAREABOARDSERIALNUMBER = 'boardinfoarea.boardserialnumber'
BOARDINFOAREABOARDPARTNUMBER = 'boardinfoarea.boardpartnumber'
BOARDINFOAREAFRUFILEID = 'boardinfoarea.frufileid'

PRODUCTINFOAREAISPRESENT = "productInfoArea.ispresent"
PRODUCTINFOAREAPRODUCTMANUFACTURER = 'productinfoarea.productmanufacturer'
PRODUCTINFOAREAPRODUCTNAME = 'productinfoarea.productname'
PRODUCTINFOAREAPRODUCTPARTMODELNAME = 'productinfoarea.productpartmodelname'
PRODUCTINFOAREAPRODUCTVERSION = 'productinfoarea.productversion'
PRODUCTINFOAREAPRODUCTSERIALNUMBER = 'productinfoarea.productserialnumber'
PRODUCTINFOAREAPRODUCTASSETTAG = 'productinfoarea.productassettag'
PRODUCTINFOAREAFRUFILEID = 'productinfoarea.frufileid'   
__DEBUG__ = "N"

conf = None


def e_print(err):
    print("ERROR: " + err)


def d_print(debug_info):
    if(__DEBUG__ == "Y"):
        print(debug_info)


def p_print(prompt):
    print("PROMPT: " + prompt)


class BaseArea():
    __childList = None

    def __init__(self, name="", size=0, offset=0):
        self.__childList = []
        self._offset = offset
        self.name = name
        self._size = size
        self._isPresent = False 
        self._data = b'\x00' * size
        self.__dataoffset = 0       
        
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

    
class BoardInfoArea(BaseArea):  

    def decodedata(self):        
        index = 0
        self.areaversion = self.data[index]  # 0
        index += 1
        print "decode length :%d class size:%d" % ((ord(self.data[index]) * 8), self.size)  # 1        
        index += 2  # 2 language skip
               
        # mfg time
        timetmp = self.data[index: index + 3]
        self.mfg_date = ord(timetmp[0]) | (ord(timetmp[1]) << 8) | (ord(timetmp[2]) << 16)
        print "decode getMfgRealData :%s" % self.getMfgRealData() 
        index += 3
        
        templen = E2Util.decodeLength(self.data[index])
        self.boardManufacturer = self.data[index + 1 : index + templen + 1 ]
        index += templen + 1
        print "decode boardManufacturer:%s" % self.boardManufacturer     
        
        templen = E2Util.decodeLength(self.data[index])
        self.boradProductName = self.data[index + 1 : index + templen + 1 ]
        index += templen + 1        
        print "decode boradProductName:%s" % self.boradProductName
        
        templen = E2Util.decodeLength(self.data[index])
        self.boardSerialNumber = self.data[index + 1 : index + templen + 1 ]
        index += templen + 1
        print "decode boardSerialNumber:%s" % self.boardSerialNumber
        
        templen = E2Util.decodeLength(self.data[index])
        self.boardPartNumber = self.data[index + 1 : index + templen + 1 ]
        index += templen + 1
        print "decode boardPartNumber:%s" % self.boardPartNumber          
        
        templen = E2Util.decodeLength(self.data[index])
        self.FRUFileID = self.data[index + 1 : index + templen + 1 ]
        index += templen + 1        
        print "decode FRUFileID:%s" % self.FRUFileID
        pass

    def recalcute(self):
        d_print("BoardInfoArea version:%x" % ord(self.boardversion))
        d_print("BoardInfoArea length:%d" % self.size)
        d_print("BoardInfoArea language:%x" % self.language)  
        self.mfg_date = E2Util.minToData() 
        d_print("BoardInfoArea mfg_date:%x" % self.mfg_date)        
        
        self.data = chr(ord(self.boardversion)) + chr(self.size / 8) + chr(self.language)
        
        self.data += chr(self.mfg_date & 0xFF)
        self.data += chr((self.mfg_date >> 8) & 0xFF)
        self.data += chr((self.mfg_date >> 16) & 0xFF)
                
        d_print("BoardInfoArea boardManufacturer:%s" % self.boardManufacturer)   
        typelength = E2Util.getTypeLength(self.boardManufacturer);
        self.data += chr(typelength)
        self.data += self.boardManufacturer
        
        self.data += chr(E2Util.getTypeLength(self.boradProductName))
        self.data += self.boradProductName
        
        self.data += chr(E2Util.getTypeLength(self.boardSerialNumber))
        self.data += self.boardSerialNumber
        
        self.data += chr(E2Util.getTypeLength(self.boardPartNumber))
        self.data += self.boardPartNumber  
           
        self.data += chr(E2Util.getTypeLength(self.FRUFileID))
        self.data += self.FRUFileID    
                
        self.data += chr(0xc1);
        d_print("self.data:%d" % len(self.data))        
        d_print("self.size:%d" % self.size)                         
        for tianchong in range(self.size - len(self.data) - 1):
            self.data += INITVALUE
            
        test = 0
        for index in range(len(self.data)):
            test += ord(self.data[index])   
        
        # checksum
        checksum = 0x100 - (test % 256)
        d_print("board info checksum:%x" % checksum)               
        self.data += chr(checksum)

    def getMfgRealData(self):                      
        starttime = datetime(1996, 1, 1, 0, 0, 0)
        # endtime = datetime.now()
        mactime = starttime + timedelta(minutes=self.mfg_date)
        return mactime
        
    @property
    def language(self):        
        self._language = 25;  
        return self._language;   
            
    @property
    def mfg_date(self):       
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
    
    def decodedata(self):
        index = 0
        self.areaversion = self.data[index]  # 0
        index += 1
        print "decode length %d" % (ord(self.data[index]) * 8)  # 1        
        print "class size %d" % self.size 
        index += 2  # 2 language skip
        
        templen = E2Util.decodeLength(self.data[index])
        self.productManufacturer = self.data[index + 1 : index + templen + 1 ]
        index += templen + 1
        print "decode productManufacturer:%s" % self.productManufacturer     
        
        templen = E2Util.decodeLength(self.data[index])
        self.productName = self.data[index + 1 : index + templen + 1 ]
        index += templen + 1        
        print "decode productName:%s" % self.productName
        
        templen = E2Util.decodeLength(self.data[index])
        self.productPartModelName = self.data[index + 1 : index + templen + 1 ]
        index += templen + 1
        print "decode productPartModelName:%s" % self.productPartModelName
        
        templen = E2Util.decodeLength(self.data[index])
        self.productVersion = self.data[index + 1 : index + templen + 1 ]
        index += templen + 1
        print "decode productVersion:%s" % self.productVersion
        
        templen = E2Util.decodeLength(self.data[index])
        self.productSerialNumber = self.data[index + 1 : index + templen + 1 ]
        index += templen + 1
        print "decode productSerialNumber:%s" % self.productSerialNumber
        
        templen = E2Util.decodeLength(self.data[index])
        self.productAssetTag = self.data[index + 1 : index + templen + 1 ]
        index += templen + 1
        print "decode productAssetTag:%s" % self.productAssetTag
        
        templen = E2Util.decodeLength(self.data[index])
        self.FRUFileID = self.data[index + 1 : index + templen + 1 ]
        index += templen + 1        
        print "decode FRUFileID:%s" % self.FRUFileID

    @property
    def productVersion (self):
        return self._productVersion;

    @property
    def areaversion (self):
        self._areaversion = COMMON_HEAD_VERSION;
        return self._areaversion; 

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
          
    def recalcute(self):
        d_print("product version:%x" % ord(self.areaversion))
        d_print("product length:%d" % self.size)
        d_print("product language:%x" % self.language)        
        self.data = chr(ord(self.areaversion)) + chr(self.size / 8) + chr(self.language)
                
        d_print("product boardManufacturer:%s" % self.productManufacturer)   
        typelength = E2Util.getTypeLength(self.productManufacturer);
        self.data += chr(typelength)
        self.data += self.productManufacturer        
        d_print("encode productManufacturer:%s" % self.productManufacturer)
        
        self.data += chr(E2Util.getTypeLength(self.productName))
        self.data += self.productName
        d_print("encode productName:%s" % self.productName)
        
        self.data += chr(E2Util.getTypeLength(self.productPartModelName))
        self.data += self.productPartModelName       
        d_print("encode productPartModelName:%s" % self.productPartModelName)
        
        self.data += chr(E2Util.getTypeLength(self.productVersion))
        self.data += self.productVersion  
        d_print("encode productVersion:%s" % self.productVersion)
        
        self.data += chr(E2Util.getTypeLength(self.productSerialNumber))
        self.data += self.productSerialNumber  
        d_print("encode productSerialNumber:%s" % self.productSerialNumber)
                   
        self.data += chr(E2Util.getTypeLength(self.productAssetTag))
        self.data += self.productAssetTag    
        d_print("encode productAssetTag:%s" % self.productAssetTag)
        
        self.data += chr(E2Util.getTypeLength(self.FRUFileID))
        self.data += self.FRUFileID    
        d_print("encode FRUFileID:%s" % self.FRUFileID)
                
        self.data += chr(0xc1);
        d_print("self.data:%d" % len(self.data))        
        d_print("self.size:%d" % self.size)                         
        for tianchong in range(self.size - len(self.data) - 1):
            self.data += INITVALUE            
        test = 0
        for index in range(len(self.data)):
            test += ord(self.data[index])        
        checksum = 0x100 - (test % 256)
        d_print("board info checksum:%x" % checksum)               
        self.data += chr(checksum)

    
class MultiRecordArea(BaseArea):
    pass


class Field():

    def __init__(self, fieldType="ASCII", fieldData=""):
        self.fieldData = fieldData
        self.fieldType = fieldType        
    
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
    _internalUserAreaOffset = None
    _InternalUseArea = None
    _ChassisInfoArea = None
    _multiRecordArea = None
    _chassicInfoAreaOffset = None
    _multiRecordAreaOffset = None
    
    def decodeBin(self, eeprom):
        commonHead = eeprom[0:8]
        # printbinvalue(commonHead)
        print("decode version %x" % ord(commonHead[0]))
        if COMMON_HEAD_VERSION != commonHead[0]:
            print "not equal"
        if E2Util.checksum(commonHead[0:7]) != ord(commonHead[7]):
            print "check sum error"
        if commonHead[1] != INITVALUE:
            d_print("Internal Use Area is present")
            self.InternalUseArea.isPresent = True
            self.internalUserAreaOffset = ord(commonHead[1])
            self.InternalUseArea.data = eeprom[self.internalUserAreaOffset * 8 : (self.internalUserAreaOffset * 8 + self.InternalUseArea.size)]
        if commonHead[2] != INITVALUE:
            d_print("Chassis Info Area is present")
            self.ChassisInfoArea.isPresent = True
            self.chassicInfoAreaOffset = ord(commonHead[2])      
            self.ChassisInfoArea.data = eeprom[self.chassicInfoAreaOffset * 8 : (self.chassicInfoAreaOffset * 8 + self.ChassisInfoArea.size)]
        if commonHead[3] != INITVALUE:
            d_print("Board Info Area is present")
            self.BoardInfoArea.isPresent = True
            self.boardInfoAreaOffset = ord(commonHead[3])
            self.BoardInfoArea.data = eeprom[self.boardInfoAreaOffset * 8 : (self.boardInfoAreaOffset * 8 + self.BoardInfoArea.size)]
            self.BoardInfoArea.decodedata();
        if commonHead[4] != INITVALUE:
            d_print("Product Info Area is present")
            self.ProductInfoArea.isPresent = True
            self.productinfoAreaOffset = ord(commonHead[4])
            self.ProductInfoArea.data = eeprom[self.productinfoAreaOffset * 8 : (self.productinfoAreaOffset * 8 + self.ProductInfoArea.size)]
            self.ProductInfoArea.decodedata();
        if commonHead[5] != INITVALUE:
            d_print("MultiRecord record present")
            self.MultiRecordArea.isPresent = True
            self.multiRecordAreaOffset = ord(commonHead[5])
            self.MultiRecordArea.data = eeprom[self.multiRecordAreaOffset * 8 : (self.multiRecordAreaOffset * 8 + self.MultiRecordArea.size)]

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
        internaluserarea = InternalUseArea(name="Internal Use Area", size=SUGGESTED_SIZE_INTERNAL_USE_AREA)     
        chassinfoarea = ChassisInfoArea(name="Chassis Info Area", size=SUGGESTED_SIZE_CHASSIS_INFO_AREA)
        boardinfoarea = BoardInfoArea(name="Board Info Area", size=SUGGESTED_SIZE_BOARD_INFO_AREA)     
        productInfoArea = ProductInfoArea(name="Product Info Area ", size=SUGGESTED_SIZE_PRODUCT_INFO_AREA)   
        multiRecordArea = MultiRecordArea(name="MultiRecord record Area ")    
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
        d_print("common Header %d" % self.offset)
        if self.InternalUseArea != None and self.InternalUseArea.isPresent:            
            self.internalUserAreaOffset = self.offset / 8
            self.offset += SUGGESTED_SIZE_INTERNAL_USE_AREA   
            d_print("InternalUseArea is present offset:%d" % self.offset)            
        if self.ChassisInfoArea != None and self.ChassisInfoArea.isPresent:
            self.chassicInfoAreaOffset = self.offset / 8
            self.offset += SUGGESTED_SIZE_CHASSIS_INFO_AREA 
            d_print("ChassisInfoArea is present offset:%d" % self.offset) 
        if self.BoardInfoArea != None and self.BoardInfoArea.isPresent:
            self.boardInfoAreaOffset = self.offset / 8
            self.offset += SUGGESTED_SIZE_BOARD_INFO_AREA
            d_print("BoardInfoArea is present offset:%d" % self.offset) 
        if self.ProductInfoArea != None and self.ProductInfoArea.isPresent:          
            self.productinfoAreaOffset = self.offset / 8
            self.offset += SUGGESTED_SIZE_PRODUCT_INFO_AREA  
            d_print("ProductInfoArea is present offset:%d" % self.offset) 
        if self.MultiRecordArea != None and self.MultiRecordArea.isPresent:
            self.multiRecordAreaOffset = self.offset / 8
            d_print("MultiRecordArea is present offset:%d" % self.offset) 
        
        if self.internalUserAreaOffset == INITVALUE:
            self.internalUserAreaOffset = 0
        if self.productinfoAreaOffset == INITVALUE :
            self.productinfoAreaOffset = 0
        if self.chassicInfoAreaOffset == INITVALUE:
            self.chassicInfoAreaOffset = 0            
        if self.boardInfoAreaOffset == INITVALUE:
            self.boardInfoAreaOffset = 0
        if self.multiRecordAreaOffset == INITVALUE:
            self.multiRecordAreaOffset = 0
        self.zeroCheckSum = 0x100 - ord(self.version) - self.internalUserAreaOffset - self.chassicInfoAreaOffset - self.productinfoAreaOffset \
                            -self.boardInfoAreaOffset - self.multiRecordAreaOffset
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
            self.ProductInfoArea.recalcute()
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


class E2Util():

    @staticmethod
    def loadconfig():
        global conf
        conf = E2Config()

    @staticmethod
    def createFruBin(filename, boardinfoarea , productInfoArea):    
        fru = CommonArea()
        fru.initDefault()             
        
        if boardinfoarea != None:                      
            fru.BoardInfoArea = boardinfoarea
        if productInfoArea != None:  
            fru.ProductInfoArea = productInfoArea
        
        # fru.ProductInfoArea.isPresent = True
        # fru.MultiRecordArea.isPresent = True
        fru.recalcute()    
        # E2Util.printbinvalue(fru.bindata) 
        E2Util.write_bin_file(filename, fru.bindata) 

    @staticmethod
    def createpartbin(part):
        try:
            boardinfoarea = None
            productInfoArea = None
            
            boradispresent = conf.getProductName(BOARDINFOAREAISPRESETN, part)
            if (boradispresent == "1"):
                boardinfoarea = BoardInfoArea(name="Board Info Area",
                                              size=SUGGESTED_SIZE_BOARD_INFO_AREA)  
                boardinfoarea.isPresent = True             
                boardinfoarea.boardManufacturer = conf.getProductName(BOARDINFOAREABOARDMANUFACTURER, part)
                boardinfoarea.boradProductName = conf.getProductName(BOARDINFOAREABORADPRODUCTNAME, part)
                boardinfoarea.boardSerialNumber = conf.getProductName(BOARDINFOAREABOARDSERIALNUMBER, part)
                boardinfoarea.boardPartNumber = conf.getProductName(BOARDINFOAREABOARDPARTNUMBER, part)
                boardinfoarea.FRUFileID = conf.getProductName(BOARDINFOAREAFRUFILEID, part)
                        
            productispresent = conf.getProductName(PRODUCTINFOAREAISPRESENT, part)
            if (productispresent == "1"):
                productInfoArea = ProductInfoArea(name="Product Info Area ",
                                                                  size=SUGGESTED_SIZE_PRODUCT_INFO_AREA)   
                productInfoArea.isPresent = True
             
                productInfoArea.productManufacturer = conf.getProductName(PRODUCTINFOAREAPRODUCTMANUFACTURER, part)
                productInfoArea.productName = conf.getProductName(PRODUCTINFOAREAPRODUCTNAME, part)
                productInfoArea.productPartModelName = conf.getProductName(PRODUCTINFOAREAPRODUCTPARTMODELNAME, part)
                productInfoArea.productVersion = conf.getProductName(PRODUCTINFOAREAPRODUCTVERSION, part)
                productInfoArea.productSerialNumber = conf.getProductName(PRODUCTINFOAREAPRODUCTSERIALNUMBER, part)
                productInfoArea.productAssetTag = conf.getProductName(PRODUCTINFOAREAPRODUCTASSETTAG, part)
                productInfoArea.FRUFileID = conf.getProductName(PRODUCTINFOAREAFRUFILEID, part)
            filename = conf.getPartBinName(part)
            E2Util.createFruBin(filename, boardinfoarea, productInfoArea)         
        except Exception as e:
            print e

    @staticmethod
    def checksum(b):
        result = 0
        for i in range(len(b)):
            result += ord(b[i])
        return 0x100 - result % 256

    @staticmethod
    def decodeLength(value):    
        a = bitarray(8)
        a.setall(True)    
        a[0:1] = 0
        a[1:2] = 0
        x = ord(a.tobytes())
        return x & ord(value)    
    
    @staticmethod
    def getTypeLength(value):        
        a = bitarray(8)
        a.setall(False)
        a[0:1] = 1
        a[1:2] = 1
        x = ord(a.tobytes())
        return  x | len(value)  
    
    @staticmethod
    def minToData():         
        starttime = datetime(1996, 1, 1, 0, 0, 0)
        endtime = datetime.now()
        seconds = (endtime - starttime).total_seconds()
        mins = seconds / 60
        m = int(round(mins))
        return m  

    @staticmethod        
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

    @staticmethod 
    def write_bin_file(filename, _value):
        retname = filename 
        filep = open(retname, 'wb')
        for x in _value:
            filep.write(str(x))
        filep.close();

    @staticmethod
    def getRemoteConfig(url):
        res = requests.get(url)    
        print res.content 
        f = open('bin.conf', 'w')
        f.write(res.content)
        return res.text


class E2Config():
    _CONFIG_PRODUCT_SECTON = "products"
    _CONFIG_TYPENAME_SECTON = "typename"
    
    def __init__(self):
        cf = ConfigParser.ConfigParser()        
        cf.read(CONFIG_FILE)
        self.configparse = cf
        self.Sections = cf.sections()
        self.ProductsTypes = cf.options(self._CONFIG_PRODUCT_SECTON)             
    
    def getProductPartItem(self, section):
        return self.configparse.options(section)
    
    def getPartBinName(self, part):        
        part = part.rstrip()
        fileprename = self.getProductName(part[-1:] , self._CONFIG_TYPENAME_SECTON)
        return (part + "_" + fileprename + ".bin").lower().replace("-", "_")       
    
    def getProductName(self, name , section=_CONFIG_PRODUCT_SECTON):
        try:
            return self.configparse.get(section, name) 
        except Exception:
            return None   
        
    def loadFile(self):
        pass       
    
    def getProductSections(self, typeindex):
        typename = self.getProductName(typeindex)
        return  filter(lambda x: typename in x, self.Sections)
        
    @property
    def ProductsTypes(self):
        return self._productTypes
    
    @property
    def Sections(self):
        return self._sections   
    
    @property
    def configparse(self):
        return self._configparse     


def main(arg):
    '''create bin'''        
    E2Util.loadconfig();    
    if len(arg) < 1:
        usage();
        sys.exit(1)
    producttype = arg[0]
    if producttype not in conf.ProductsTypes:
        usage();
        sys.exit(1)   
    
    productParts = conf.getProductSections(producttype)
    print "产品名称: %s" % conf.getProductName(producttype)
    if len(productParts) <= 0:
        print "没有配置项"
    for part in productParts:
        print "生成文件: %s" % conf.getPartBinName(part)        
        E2Util.createpartbin(part)    
    

def usage():
    print("Usage: [e2.py product ]");
    print("       example: e2.py 1  ");
    print("   userless-product :");
    for card in conf.ProductsTypes:
        print "        %s %s" % (card , conf.getProductName(card));

    
if __name__ == '__main__':   
    # main(sys.argv[1:])
    main(["1"])
    pass
