import xml.etree.ElementTree as ET
from datetime import datetime
from .models import *

def buildXML(project):
    '''
        Generate the XML file and return it...
    '''

    projectName = project.name
    root = getRoot(projectName)

    # controller
    projId = project.id
    processorType = ProjModule.objects.filter(projId=projId).get(moduleId__type='Processor').catalogNumber
    controller = ET.SubElement(root,'Controller')
    controller = getController(controller,projectName,processorType)

    # redundancy
    redundancyInfo = buildSubElement(controller,'RedundancyInfo',{'KeepTestEditsOnSwitchOver':'false','Enabled':'false'})
    security = buildSubElement(controller,'Security',{'ChangesToDetect':'16#ffff_ffff_ffff_ffff','Code':'0'})
    safetyInfo = buildSubElement(controller,'SafetyInfo',{})
    dataTypes = buildSubElement(controller,'DataTypes',{})

    # modules...
    # 1st is the controller module
    modules = ET.SubElement(controller,'Modules')
    # TODO: Make this variable
    chassisSize = 17
    module = getControllerModule(processorType,chassisSize)
    modules.append(module)
    #local Modules
    localModules = ProjModule.objects.filter(projId=projId).filter(parent='Local')
    # TODO: This is temp just for testing, should come from props
    ipAddress = '192.168.1.1'
    for module in localModules:
        if module.moduleId.type != 'Processor':
            #m =  getModuleXml(catalogNumber=module['catalogNumber'],moduleName=module['moduleName'],slotNumber=module['slot'])
            # TODO: This is temp just for testing, should come from props
            if module.moduleId.type == 'Communications':
                m =  getModuleXml(module.moduleId.catalogNumber,moduleName=module.name,slotNumber=module.slot,ipAddress=ipAddress)
                ipAddress = incrementIp(ipAddress)
            else:
                m =  getModuleXml(module.moduleId.catalogNumber,moduleName=module.name,slotNumber=module.slot)
            modules.append(m)
    # child modules.
    filter = {'projId__exact':projId}
    childModules = ProjModule.objects.filter(**filter).exclude(parent='Local')
    for module in childModules:
        # TODO make this more flexible
        if module.moduleId.catalogNumber == '1734-AENT':
            chassisSize = module.chassisId.catalogId.size
            m =  getModuleChassisXML(catalogNumber=module.moduleId.catalogNumber,moduleName=module.name,parentModule=module.parent,slotNumber=module.slot,chassisSize=chassisSize,ipAddress=ipAddress,isEthernet=True)
            ipAddress = incrementIp(ipAddress)
        else:
            m =  getModuleXml(catalogNumber=module.moduleId.catalogNumber,moduleName=module.name,slotNumber=module.slot,parentModule=module.parent)
        modules.append(m)
    return root

def incrementIp(ipAddress):
    '''
        Increment the ip address by 1 and return it
    '''
    octets = ipAddress.split('.')
    n = int(octets[3]) + 1
    octets[3] = str(n)
    ipAddress = '.'.join(octets)
    return ipAddress

def getModuleXml(catalogNumber,moduleName,slotNumber,isEthernet=False,ipAddress=None,parentModule='Local',chassisSize=None):
	'''
		Get a modules xml from the db and return it after attempting to set any passed attributes
		Return an xml element

	'''

	# no spaces or dashes
	moduleName = moduleName.replace(' ','_')
	moduleName = moduleName.replace('-','_')

	xml = Module.objects.get(catalogNumber=catalogNumber).xml
	if xml is None:
		# print 'Item ',catalogNumber,' not found!'
		return None
	else:
		tree = ET.fromstring(xml)
	tree.set('Name',moduleName)
	if parentModule != 'Local':
		tree.set('ParentModule',parentModule)
	for child in tree:
		if child.tag == 'Ports':
			for port in child:
				if port.attrib['Type'] in ('ICP','PointIO') :
					port.set('Address',str(slotNumber))
				if port.attrib['Type'] == 'Ethernet' and isEthernet:
					port.set('Address',ipAddress)
				if chassisSize is not None and port.attrib['Type'] == 'PointIO':
					for pchild in port:
						if pchild.tag == 'Bus':
							pchild.set('Size',chassisSize)

	return tree

def getModuleChassisXML(catalogNumber,moduleName,slotNumber,isEthernet=False,ipAddress=None,parentModule='Local',chassisSize=None):
	'''
		Get a modules xml from the db and return it after attempting to set any passed attributes
		This is for modules like point I/O adapters that have particular chassis size related footprints.
		Return an xml element

	'''

	# no spaces or dashes
	moduleName = moduleName.replace(' ','_')
	moduleName = moduleName.replace('-','_')

	xml = Chassis.objects.filter(catalogNumber=catalogNumber).get(size=chassisSize).xml

	if xml == '':
		# print 'Item ',catalogNumber,' not found!'
		return None
	else:
		tree = ET.fromstring(xml)
		tree.set('Name',moduleName)
		if parentModule != 'Local':
			tree.set('ParentModule',parentModule)
		for child in tree:
			if child.tag == 'Ports':
				for port in child:
					if port.attrib['Type'] == 'ICP':
						port.set('Address',str(slotNumber))
					if port.attrib['Type'] == 'Ethernet' and isEthernet:
						port.set('Address',ipAddress)
					if chassisSize is not None and port.attrib['Type'] == 'PointIO':
						for pchild in port:
							if pchild.tag == 'Bus':
								pchild.set('Size',str(chassisSize))
	return tree


def getModuleXml(catalogNumber,moduleName,slotNumber,isEthernet=False,ipAddress=None,parentModule='Local',chassisSize=None):
	'''
		Get a modules xml from the db and return it after attempting to set any passed attributes
		Return an xml element

	'''

	# no spaces or dashes
	moduleName = moduleName.replace(' ','_')
	moduleName = moduleName.replace('-','_')

	xml = Module.objects.get(catalogNumber=catalogNumber).xml
	if xml is None:

		return None
	else:
		tree = ET.fromstring(xml)
	tree.set('Name',moduleName)
	if parentModule != 'Local':
		tree.set('ParentModule',parentModule)
	for child in tree:
		if child.tag == 'Ports':
			for port in child:
				if port.attrib['Type'] in ('ICP','PointIO') :
					port.set('Address',str(slotNumber))
				if port.attrib['Type'] == 'Ethernet' and isEthernet:
					port.set('Address',ipAddress)
				if chassisSize is not None and port.attrib['Type'] == 'PointIO':
					for pchild in port:
						if pchild.tag == 'Bus':
							pchild.set('Size',chassisSize)

	return tree

def getControllerModule(catalogNumber,chassisSize):
	'''
		Add the controller module to the passed element and return it...
	'''

	attribs = {}
	attribs['Name'] = 'Local'
	attribs['CatalogNumber'] = catalogNumber
	attribs['Vendor'] = '1'
	attribs['ProductType'] = '14'
	attribs['ProductCode'] = '164'
	attribs['Major'] = '32'
	attribs['Minor'] = '11'
	attribs['ParentModule'] = 'Local'
	attribs['ParentModPortId'] = '1'
	attribs['Inhibited'] = 'false'
	attribs['MajorFault'] = 'true'

	module = buildElement('Module',attribs)

	# electronic keying
	eKey = ET.SubElement(module,'Ekey')
	eKey.set('State','Disabled')

	# ports, an list of ports
	ports = ET.SubElement(module,'Ports')
	p0 = buildElement('Port',{'Upstream':'false','Type':'ICP','Address':'0','Id':'1'})
	p0p = buildSubElement(p0,'Bus',{'Size':str(chassisSize)})  													# This is the chassis size
	ports.append(p0)
	ports.append(buildElement('Port',{'Upstream':'false','Type':'Ethernet','Id':'2'}))
	return module


def getController(controller,name,processorType):
	'''
		Build a controller element and return it
	'''

	attribs = {}
	attribs['Use'] = 'Target'
	attribs['Name'] = 'Test'
	attribs['ProcessorType'] = processorType
	attribs['MajorRev'] = '32'
	attribs['MinorRev'] = '11'
	attribs['ProjectCreationDate'] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
	attribs['LastModifiedDate'] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
	attribs['SFCExecutionControl'] = 'CurrentActive'
	attribs['SFCRestartPosition'] = 'MostRecent'
	attribs['SFCLastScan'] = 'DontScan'
	attribs['ProjectSN'] = '16#0000_0000'
	attribs['MatchProjectToController'] = 'false'
	attribs['CanUseRPIFromProducer'] = 'false'
	attribs['InhibitAutomaticFirmwareUpdate'] = '0'
	attribs['PassThroughConfiguration'] = 'EnabledWithAppend'
	attribs['DownloadProjectDocumentationAndExtendedProperties'] = 'true'
	attribs['DownloadProjectCustomProperties'] = 'true'
	attribs['ReportMinorOverflow'] = 'false'

	for key in attribs:
		controller.set(key,attribs[key])
	return controller

def getRoot(projectName,softwareRevision='32.00',nodeName='RsLogix5000Content'):
	'''
		Build and return the root node

	'''
	# hardcoding some attributes for now.
	attribs = {}
	attribs['SchemaRevision'] = "1.0"
	attribs['SoftwareRevision'] = softwareRevision
	attribs['TargetName'] = projectName
	attribs['TargetType'] = 'Controller'
	attribs['ContainsContext'] = 'false'
	attribs['Owner'] = 'Bastian Solutions'
	attribs['ExportDate'] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
	attribs['ExportOptions'] = "NoRawData L5KData DecoratedData ForceProtectedEncoding AllProjDocTrans"

	root = buildElement(nodeName,attribs)
	return root

def buildElement(name,attribs):

	element = ET.Element(name)
	for key in attribs:
		element.set(key,attribs[key])
	return element

def buildSubElement(parent,name,attribs):
	'''
		Adds a sub element to the parent, sets it's attribs
	'''
	subElement = ET.SubElement(parent,name)
	for key in attribs:
		subElement.set(key,attribs[key])
	return parent
