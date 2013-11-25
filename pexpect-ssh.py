#!/usr/bin/env python
import pexpect, termios
import struct, fcntl, os, sys, signal
import xml.etree.cElementTree as ET
tree = ET.parse('netdevices.xml')
root= tree.getroot()
#root = ET.Element("NetDevices")
#ipAddress=ipAddr
def sigwinch_passthrough (sig, data):
    # Check for buggy platforms (see pexpect.setwinsize()).
    if 'TIOCGWINSZ' in dir(termios):
        TIOCGWINSZ = termios.TIOCGWINSZ
    else:
        TIOCGWINSZ = 1074295912 # assume
    s = struct.pack ("HHHH", 0, 0, 0, 0)
    a = struct.unpack ('HHHH', fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ , s))
    global global_pexpect_instance
    global_pexpect_instance.setwinsize(a[0],a[1])

def updateMac(updateInterface,updateMac):
    xmlInterface= ET.SubElement(device,"interface")
    xmlInterface.text=updateInterface
    MACTable=ET.SubElement(xmlInterface,"mactable")
    MACTable.text=updateMac
    tree = ET.ElementTree(root)
    tree.write("netdevices.xml")

def updateDB(updateSerial,updateVersion):

    xmlVersion=ET.SubElement(device,"version")
    xmlVersion.text=updateVersion
    xmlSerial=ET.SubElement(device,"serial")
    xmlSerial.text=updateSerial
    
    tree = ET.ElementTree(root)
    tree.write("netdevices.xml")
ipAddr=sys.argv[1]
    
ssh_newkey = 'Are you sure you want to continue connecting'
p=pexpect.spawn('ssh administrator@'+ipAddr)
i=p.expect([ssh_newkey,'password:',pexpect.EOF,pexpect.TIMEOUT],1)
if i==0:
    print "I say yes"
    p.sendline('yes')
    i=p.expect([ssh_newkey,'password:',pexpect.EOF])
if i==1:
    print "I give password",
    p.sendline("Carb0nDay")
elif i==2:
    print "I either got key or connection timeout"
    pass
elif i==3: #timeout
    pass
p.sendline("\r")
global global_pexpect_instance
global_pexpect_instance = p
signal.signal(signal.SIGWINCH, sigwinch_passthrough)
c=p.expect(['Enterasys','Extreme','HEWLETT-PACKARD',pexpect.EOF])
if c==0:
    print ('its enterasys')
    p.sendline('set length 0')
    p.sendline('show mac')
    p.sendline('exit')
if c==2:
    print ('its HP')
    p.sendline('\n')
    p.sendline('terminal length 1000')
    p.sendline('show system information')
    p.sendline('show mac-address')
    d=p.expect(['MORE','#',pexpect.EOF])
    if d==0:
        p.sendline('\s')
    p.sendline('exit')
    p.sendline('exit')
    e=p.expect(['Do you want to log out [y/n]','#',pexpect.EOF])
    if e==0:
        p.sendline('y')
i=p.expect ([pexpect.EOF])
a=0
if i==0 and c==0:
    f=open('testfile.txt','w')
    MAC = p.before
    f.write(MAC)
    f.close()
    g=open('macaddresses.txt','w')
    hostName='000'
    f=open('testfile.txt','r')
    foundSN=1 #to look for SN in DB
    foundMAC=1#look for mac
    inSerialLine=0#to see if already acquired serial number
    changesMade=0#changes made to DB
    vendor='unknown'
    lineNumber=0
    

    for line in f:#find serial number firmware and mac addresses in file
        lineNumber=lineNumber+1
        if lineNumber==7:
            description=line
            description=description.strip('\s\t\n\r')
        if "->" in line and foundSN==1 and hostName=='000':
            hostName=line.split("(su)->")[0]
            foundDevice.set('nodeName',hostName)
            print('hostnameFound')
        #print ('going through loop')
        if "Serial" in line:
            print 'going thru serial line'
            inSerialLine=1
            foundSN=0 #to look for SN in DB
            head,sep,serialNumber=line.partition(":")
            serialNumber=serialNumber.strip(' \s\t\n\r')
            print serialNumber
            for item in root:
                device=item
                print device.find('serial').text
                if device.find('serial').text==serialNumber:
                    foundDevice=device
                    print 'found device'
                    #if foundDevice.get('nodeName')!=ipAddress:
                    #foundDevice.set('nodeName',ipAddress)
                    #changesMade=1
                    mactable=foundDevice.find('mactable')
                    foundDevice.remove(mactable)
                    mactableInsert=ET.SubElement(foundDevice,'mactable')
                    foundSN=1

    
        if "Firmware" in line and foundSN==1:
            changesMade=1
            head,sep,firmwareVersion=line.partition(":")
            firmwareVersion=firmwareVersion.strip(' \s\t\n\r')
            print firmwareVersion
            version=foundDevice.find('version')
            if firmwareVersion!=version.text:
                version.text=firmwareVersion
                #update DB with new version if found SN
        if "Enterasys" in line:
            vendor='Enterasys'
    
        if "Learned" in line and foundSN==1:
            #print ('found new mac')
            interfaceNeverFound=1#to see if new interface or just uplink
            vlanNeverFound=1
            #sameInterface=0#to see if new interface or just uplink
            foundMAC=0#look for mac
            macAddress=line[0:17]
            g.write(macAddress+',')
            interface=line[23:37]
            interface=interface.strip(' \s\t\n\r')
            vlan=line[18:22]
            vlan=vlan.strip(' \s\t\n\r')
            g.write(interface)
            #deviceInterface=foundDevice.find('interface')
            if interface!='tg.1.50':#uplink interface ignored
                for mac in foundDevice.iter('mac'):
                    #print('itering mac addresses')
                    #print mac.get('name')
                    if mac.get('name')==macAddress:
                        for int in mac:
                            #print('itering through interfaces')
                            print interface
                            print mac.get('name')
                            if int.get('number')==interface:
                                foundMAC=1
                                interfaceNeverFound=0
                                for vlanCheck in int:
                                    #print ('itering through vlans')
                                    print vlanCheck.get('tag')
                                    if vlanCheck.get('tag')==vlan:
                                        print('match')
                                        vlanNeverFound=0
                            if interfaceNeverFound==1:
                                #print('int never found')
                                print vlan
                                print int.text
                                #mac.remove(int)
                                interfaceInsert=ET.SubElement(mac,'interface')
                                interfaceInsert.set('number',interface)
                                int=interfaceInsert
                                foundMAC=1
                                changesMade=1
                            if vlanNeverFound==1:
                                #print('vlan not found')
                                vlanInsert=ET.SubElement(int,'vlan')
                                vlanInsert.set('tag',vlan)
                                print vlanInsert.get('tag')
                                changesMade=1
                                foundMAC=1
            else:#ignoring uplink ports tg.1.50
                foundMAC=1

        
        
        if foundMAC==0 and foundSN==1:
            a=a+1
            print ('adding mac to list')
            print a
            changesMade=1
            #append to create child
            mactable=foundDevice.find('mactable')
            macInsert=ET.SubElement(mactable,'mac')
            macInsert.set('name',macAddress)
            interfaceInsert=ET.SubElement(macInsert,'interface')
            interfaceInsert.set('number',interface)
            vlanInsert=ET.SubElement(interfaceInsert,'vlan')
            vlanInsert.set('tag',vlan)
            #tree = ET.ElementTree(root)
            #tree.write("netdevices.xml")
            #update mac table
            foundMAC=1
        
        if foundSN==0:
            changesMade=1
            print "serial not found"
            deviceInsert=ET.SubElement(root,'device')
            deviceInsert.set('nodeName',hostName)
            ipInsert=ET.SubElement(deviceInsert,'MGT-IP')
            ipInsert.text=ipAddr
            versionInsert=ET.SubElement(deviceInsert,'version')
            versionInsert.text='000'
            if inSerialLine==0:
                serialInsert=ET.SubElement(deviceInsert,'serial')
                serialInsert.text='000'
            else:
                serialInsert=ET.SubElement(deviceInsert,'serial')
                serialInsert.text=serialNumber
            vendorInsert=ET.SubElement(deviceInsert,'vendor')
            vendorInsert.text=vendor
            descriptionInsert=ET.SubElement(deviceInsert,'description')
            descriptionInsert.text=description
            mactableInsert=ET.SubElement(deviceInsert,'mactable')
            foundDevice=deviceInsert
            changesMade=1
            #tree = ET.ElementTree(root)
            #tree.write("netdevices.xml")
            #add new device here
            foundSN=1
    if changesMade==1:
        tree = ET.ElementTree(root)
        tree.write("netdevices.xml")
    f.close()
    g.close()
            
#if switch is HP then populate it through here. 
if i==0 and c==2:
    f=open('testfile.txt','w')
    MAC = p.before
    f.write(MAC)
    f.close()
    g=open('macaddresses.txt','w')
    hostName='000'
    f=open('testfile.txt','r')
    foundSN=1 #to look for SN in DB
    foundMAC=1#look for mac
    inSerialLine=0#to see if already acquired serial number
    changesMade=0#changes made to DB
    vendor='unknown'
    lineNumber=0
    
    
    for line in f:#find serial number firmware and mac addresses in file
        lineNumber=lineNumber+1
        if lineNumber==7:
            description=line
            description=description.strip('\s\t\n\r')
        if "->" in line and foundSN==1 and hostName=='000':
            hostName=line.split("#")[0]
            foundDevice.set('nodeName',hostName)
            print('hostnameFound')
        #print ('going through loop')
        if "Serial" in line:
            print 'going thru serial line'
            inSerialLine=1
            foundSN=0 #to look for SN in DB
            head,sep,serialNumber=line.partition(":")[1]
            serialNumber=serialNumber.strip(' \s\t\n\r')
            print serialNumber
            for item in root:
                device=item
                print device.find('serial').text
                if device.find('serial').text==serialNumber:
                    foundDevice=device
                    print 'found device'
                    #if foundDevice.get('nodeName')!=ipAddress:
                    #foundDevice.set('nodeName',ipAddress)
                    #changesMade=1
                    mactable=foundDevice.find('mactable')
                    foundDevice.remove(mactable)
                    mactableInsert=ET.SubElement(foundDevice,'mactable')
                    foundSN=1
        
        
        if "Software revision  :" in line and foundSN==1:
            changesMade=1
            head,sep,firmwareVersion=line.partition(":")[0]
            firmwareVersion=firmwareVersion.strip(' \s\t\n\r')
            print firmwareVersion
            version=foundDevice.find('version')
            if firmwareVersion!=version.text:
                version.text=firmwareVersion
        #update DB with new version if found SN
        if "HEWLETT-PACKARD" in line:
            vendor='HEWLETT-PACKARD'
        
        if "Learned" in line and foundSN==1:
            #print ('found new mac')
            interfaceNeverFound=1#to see if new interface or just uplink
            vlanNeverFound=1
            #sameInterface=0#to see if new interface or just uplink
            foundMAC=0#look for mac
            macAddress=line[0:17]
            g.write(macAddress+',')
            interface=line[23:37]
            interface=interface.strip(' \s\t\n\r')
            vlan=line[18:22]
            vlan=vlan.strip(' \s\t\n\r')
            g.write(interface)
            #deviceInterface=foundDevice.find('interface')
            if interface!='tg.1.50':#uplink interface ignored
                for mac in foundDevice.iter('mac'):
                    #print('itering mac addresses')
                    #print mac.get('name')
                    if mac.get('name')==macAddress:
                        for int in mac:
                            #print('itering through interfaces')
                            print interface
                            print mac.get('name')
                            if int.get('number')==interface:
                                foundMAC=1
                                interfaceNeverFound=0
                                for vlanCheck in int:
                                    #print ('itering through vlans')
                                    print vlanCheck.get('tag')
                                    if vlanCheck.get('tag')==vlan:
                                        print('match')
                                        vlanNeverFound=0
                            if interfaceNeverFound==1:
                                #print('int never found')
                                print vlan
                                print int.text
                                #mac.remove(int)
                                interfaceInsert=ET.SubElement(mac,'interface')
                                interfaceInsert.set('number',interface)
                                int=interfaceInsert
                                foundMAC=1
                                changesMade=1
                            if vlanNeverFound==1:
                                #print('vlan not found')
                                vlanInsert=ET.SubElement(int,'vlan')
                                vlanInsert.set('tag',vlan)
                                print vlanInsert.get('tag')
                                changesMade=1
                                foundMAC=1
            else:#ignoring uplink ports tg.1.50
                foundMAC=1
        
        
        
        if foundMAC==0 and foundSN==1:
            a=a+1
            print ('adding mac to list')
            print a
            changesMade=1
            #append to create child
            mactable=foundDevice.find('mactable')
            macInsert=ET.SubElement(mactable,'mac')
            macInsert.set('name',macAddress)
            interfaceInsert=ET.SubElement(macInsert,'interface')
            interfaceInsert.set('number',interface)
            vlanInsert=ET.SubElement(interfaceInsert,'vlan')
            vlanInsert.set('tag',vlan)
            #tree = ET.ElementTree(root)
            #tree.write("netdevices.xml")
            #update mac table
            foundMAC=1
        
        if foundSN==0:
            changesMade=1
            print "serial not found"
            deviceInsert=ET.SubElement(root,'device')
            deviceInsert.set('nodeName',hostName)
            ipInsert=ET.SubElement(deviceInsert,'MGT-IP')
            ipInsert.text=ipAddr
            versionInsert=ET.SubElement(deviceInsert,'version')
            versionInsert.text='000'
            if inSerialLine==0:
                serialInsert=ET.SubElement(deviceInsert,'serial')
                serialInsert.text='000'
            else:
                serialInsert=ET.SubElement(deviceInsert,'serial')
                serialInsert.text=serialNumber
            vendorInsert=ET.SubElement(deviceInsert,'vendor')
            vendorInsert.text=vendor
            descriptionInsert=ET.SubElement(deviceInsert,'description')
            descriptionInsert.text=description
            mactableInsert=ET.SubElement(deviceInsert,'mactable')
            foundDevice=deviceInsert
            changesMade=1
            #tree = ET.ElementTree(root)
            #tree.write("netdevices.xml")
            #add new device here
            foundSN=1
    if changesMade==1:
        tree = ET.ElementTree(root)
        tree.write("netdevices.xml")
    f.close()
    g.close()

try:
    p.interact()
    sys.exit(0)
except:
    sys.exit(1)