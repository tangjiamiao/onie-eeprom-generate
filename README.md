[products] 
定义产品类型和名称 如需在后续添加 id = name
1 = AS13-48F8H 
2 = AS13-32H 
3 = AS23-128H
4 = XEON-D-C

[typename] 固定值 
#   1 TLV EEPROM  0x56      
#   2 X86 CPU EEPROM        
#   3 BMC EEPROM            
#   4 CPU底板EEPROM         
#   5 MAC板 EEPROM          
#   6.线卡 EEPROM （128有） 
#   7.风扇转接板EEPROM      
#   8.风扇小板 EEPROM       
#   9.电源FRU EEPROM       

[XEON-D-C-2]  由products中的值 + "-" + typename组成
  
   板卡boardinfoarea 
    boardinfoarea.ispresent = 1   //todo     #ispresent表示有这部分区域
    boardinfoarea.boardManufacturer = Alibaba
    boardinfoarea.boradProductName = XEON-D-C
    boardinfoarea.boardSerialNumber = 0000000000000
    boardinfoarea.boardPartNumber = XEON-D-C-100
    boardinfoarea.FRUFileID = 4-2   //todo  #FRUFILEID由products和typename组成
    
   产品
    productInfoArea.ispresent = 1
    productInfoArea.productManufacturer = Alibaba
    productInfoArea.productName = M1HFANI
    productInfoArea.productPartModelName = M1HFANI-F
    productInfoArea.productVersion = 10
    productInfoArea.productSerialNumber = 0000000000000
    productInfoArea.productAssetTag = RJ00000000001
    productInfoArea.FRUFileID = 2-8 
 