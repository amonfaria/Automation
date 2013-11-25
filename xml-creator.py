#!/usr/bin/python
import xml.etree.cElementTree as ET

root = ET.Element("NetDevices")

device = ET.SubElement(root, "NetDevices")
device.set("name","test1")

adminstatus = ET.SubElement(device, "adminstatus")
#adminstatus.set("name", "blah")
adminstatus.text = "PRODUCTION"
xmlSerial=ET.SubElement(device,"serial")
xmlSerial.text="123456"
xmlVersion=ET.SubElement(device,"version")
xmlVersion.text="1354688"
xmlInterface= ET.SubElement(device,"interface")
xmlInterface.text="3"
MACTable=ET.SubElement(device,"mactable")
MACTable.text="789456"
tree = ET.ElementTree(root)
tree.write("filename.xml")