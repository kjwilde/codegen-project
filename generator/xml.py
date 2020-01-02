import xml.etree.ElementTree as ET
from datetime import datetime
from .models import *
from .xml_helper import buildElement,buildSubElement,CDATA

def buildXML(project):
    '''
        Generate the XML file and return it...
    '''

    projectName = project.name
    root = getRoot(projectName)

    # controller
    projId = project.id
    processorType = ProjModule.objects.filter(projId=projId).get(moduleId__type__type='Processor').catalogNumber
    controller = ET.SubElement(root,'Controller')
    controller = getController(controller,projectName,processorType)

    # redundancy
    redundancyInfo = buildSubElement(controller,'RedundancyInfo',{'KeepTestEditsOnSwitchOver':'false','Enabled':'false'})
    security = buildSubElement(controller,'Security',{'ChangesToDetect':'16#ffff_ffff_ffff_ffff','Code':'0'})
    safetyInfo = buildSubElement(controller,'SafetyInfo',{})
    dataTypes = buildSubElement(controller,'DataTypes',{})

    # modules...
    # 1st is the controller module

    # IP Addresses:  For now we'll just increment private addresses to prevent RSLogix import errors.
    ipAddress = '192.168.1.1'
    modules = ET.SubElement(controller,'Modules')
    # TODO: Make this variable
    chassisSize = 17
    module = getControllerModule(processorType,chassisSize)
    modules.append(module)
    #local Modules
    localModules = ProjModule.objects.filter(projId=projId).filter(parent='Local')
    for module in localModules:
        if module.moduleId.type.type != 'Processor':
            #m =  getModuleXml(catalogNumber=module['catalogNumber'],moduleName=module['moduleName'],slotNumber=module['slot'])
            if len(module.comments) > 0:
                comments = module.comments
            else:
                comments = None
            ip = None
            if module.moduleId.type.type == 'Communications' :
                ip = ipAddress
                ipTemp = ipAddress.split('.')
                ipTemp[3] = str(int(ipTemp[3]) + 1)
                ipAddress = '.'.join(ipTemp)
            m =  getModuleXml(module.moduleId.catalogNumber,moduleName=module.name,slotNumber=module.slot,comments=comments,ipAddress=ip)
            modules.append(m)
    # child modules.
    filter = {'projId__exact':projId}
    childModules = ProjModule.objects.filter(**filter).exclude(parent='Local')
    for module in childModules:
        # TODO make this more flexible
        if module.moduleId.catalogNumber == '1734-AENT':
            chassisSize = module.chassisId.catalogId.size
            ip = ipAddress
            ipTemp = ipAddress.split('.')
            ipTemp[3] = str(int(ipTemp[3]) + 1)
            ipAddress = '.'.join(ipTemp)
            m =  getModuleChassisXML(catalogNumber=module.moduleId.catalogNumber,moduleName=module.name,parentModule=module.parent,slotNumber=module.slot,chassisSize=chassisSize,ipAddress=ip)
        else:
            if len(module.comments) > 0:
                comments = module.comments
            else:
                comments = None
            m =  getModuleXml(catalogNumber=module.moduleId.catalogNumber,moduleName=module.name,slotNumber=module.slot,parentModule=module.parent,comments=comments)
        modules.append(m)

    # tasks and programs
    # Always have two programs, input and output mapping...
    # for each chassis there'll be a corrspoinding input and output routine
    chassis = ProjChassis.objects.filter(projId=projId)
    routineNames = []
    chassisIds = []
    for i,c in enumerate(chassis):
        routineNames.append('_' + str((i+1) * 5).zfill(2) + '_' + c.name)
        chassisIds.append(c.id)

    programs = ET.SubElement(controller,'Programs')
    inputMapping = getProgram(name='InputMapping')
    routines = ET.SubElement(inputMapping,'Routines')
    mainRoutine = getRoutine(name='_00_MainRoutine')
    mainRoutine = buildMainRoutine(mainRoutine,routineNames)
    routines.append(mainRoutine)
    for i,rn in enumerate(routineNames):
        r = getRoutine(name=rn)
        r = addInputMapping(r,chassisIds[i])
        routines.append(r)

    programs.append(inputMapping)
    outputMapping = getProgram(name='OutputMapping')
    routines = ET.SubElement(outputMapping,'Routines')
    mainRoutine = getRoutine(name='_00_MainRoutine')
    mainRoutine = buildMainRoutine(mainRoutine,routineNames)
    routines.append(mainRoutine)
    for i,rn in enumerate(routineNames):
        r = getRoutine(name=rn)
        r = addOutputMapping(r,chassisIds[i])
        routines.append(r)
    programs.append(outputMapping)

    sp = ['InputMapping','OutputMapping']
    tasks = ET.SubElement(controller,'Tasks')
    mainTask = getTask(name='MainTask_20ms',rate=20.000,scheduledPrograms= sp)
    tasks.append(mainTask)
    return root

def buildMainRoutine(routine,subroutines):
    '''
        Gets a routine xml object, adds JSR rungs for each of
        the passed list of subroutines and returns the routine object
    '''

    rllContent = ET.SubElement(routine,'RLLContent')

    for rungNumber,subroutine in enumerate(subroutines):
        rung = buildElement('Rung',{'Type':'N','Number':str(rungNumber)})
        text = ET.Element('Text')
        code = CDATA('JSR(' + subroutine +',0);')
        text.append(code)
        rung.append(text)
        rllContent.append(rung)

    return routine

def addInputMapping(routine,chassisId):
    '''
        Add some basic input mapping to the passed routine and return it...
        TODO:  For the CDATA, make some sort of db entry to format for different types
                of modules something like:  I.DATA[<s>]b<bb> where s = slot and bb = bit, padded
    '''
    rllContent = ET.SubElement(routine,'RLLContent')       # holds all the rung contents...

    chassis = ProjChassis.objects.get(id=chassisId)
    local = True
    if chassis.parent != 'Local':
        local = False
    filter = {'chassisId':chassisId}
    chassisMods = ProjModule.objects.filter(**filter).order_by('slot')
    rungNumber = 0
    for mod in chassisMods:
        if  len(mod.catalogNumber) > 0 and mod.catalogNumber[5] == 'I':
            # this is somewhat contrived, need to add a property for number of points to loop through...
            for b in range(mod.moduleId.points):
                rung = buildElement('Rung',{'Type':'N','Number':str(rungNumber)})
                text = ET.Element('Text')
                slot = mod.slot
                if local:
                    code = CDATA('XIC(Local:'+ str(slot) + ':I.Data.' + str(b) + ')NOP();')
                else:
                    # This is for rack optimized data, digital I/O ...
                    name = chassisMods.get(slot=0).name
                    code = CDATA('XIC(' + name + ":" + 'I.Data[' + str(slot) + '].' + str(b) + ')NOP();')
                text.append(code)
                rung.append(text)
                rllContent.append(rung)
                rungNumber += 1
    return routine

def addOutputMapping(routine,chassisId):
    '''
        Add some basic input mapping to the passed routine and return it...
        TODO:  For the CDATA, make some sort of db entry to format for different types
                of modules something like:  I.DATA[<s>]b<bb> where s = slot and bb = bit, padded
    '''
    rllContent = ET.SubElement(routine,'RLLContent')       # holds all the rung contents...

    chassis = ProjChassis.objects.get(id=chassisId)
    local = True
    if chassis.parent != 'Local':
        local = False
    filter = {'chassisId':chassisId}
    chassisMods = ProjModule.objects.filter(**filter).order_by('slot')
    rungNumber = 0
    for mod in chassisMods:
        if  len(mod.catalogNumber) > 0 and mod.catalogNumber[5] == 'O':
            # this is somewhat contrived, need to add a property for number of points to loop through...
            for b in range(mod.moduleId.points):
                rung = buildElement('Rung',{'Type':'N','Number':str(rungNumber)})
                text = ET.Element('Text')
                slot = mod.slot
                # code = CDATA('XIC(Local:'+ str(slot) + ':I.Data.' + str(b) + ')NOP();')
                if local:
                    code = CDATA('AFI()OTE(Local:'+ str(slot) + ':O.Data.' + str(b) + ');')
                else:
                    # This is for rack optimized data, digital I/O ...
                    name = chassisMods.get(slot=0).name
                    code = CDATA('AFI()OTE('+ name + ":" + 'O.Data[' + str(slot) + '].' + str(b) + ');')
                text.append(code)
                rung.append(text)
                rllContent.append(rung)
                rungNumber += 1
    return routine




def getRoutine(name,type='RLL'):
    attribs = {'Name':name,'Type':type}
    routine = buildElement('Routine',attribs)
    return routine

def getTask(name,taskType='PERIODIC',inhibitTask=False,disableUpdateOutputs=False,watchdog=500,priority=10,rate=20,scheduledPrograms=[]):
    '''
        Build a task.  schedulePrograms is a list of program names to include
    '''
    attribs = {}
    attribs['Name'] = name
    attribs['Type'] = taskType.upper()
    attribs['InhibitTask'] = str(inhibitTask).lower()
    attribs['DisableUpdateOutputs'] = str(disableUpdateOutputs).lower()
    attribs['Watchdog'] = str(watchdog)
    attribs['Priority'] = str(priority)
    attribs['Rate'] = str(rate)
    task = buildElement('Task',attribs)
    sp = ET.SubElement(task,'ScheduledPrograms')
    for program in scheduledPrograms:
        sp.append(buildElement('ScheduledProgram',{'Name':program}))
    return task

def getProgram(name,useAsFolder=False,disabled=False,mainRoutineName='_00_MainRoutine',testEdits=False):
    attribs={}
    attribs['Name'] = name.replace(' ','_')
    attribs['UseAsFolder'] = str(useAsFolder).lower()
    attribs['Disabled'] = str(disabled).lower()
    attribs['MainRoutineName'] = mainRoutineName
    attribs['TestEdits'] = str(testEdits).lower()
    program = buildElement('Program',attribs)
    return program


def getModuleXml(catalogNumber,moduleName,slotNumber,ipAddress=None,parentModule='Local',chassisSize=None,comments=None):
    '''
     		Get a modules xml from the db and return it after attempting to set any passed attributes
             comments is a comma seperated string list of comments
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
                if port.attrib['Type'] == 'Ethernet' and ipAddress is not None:
                    port.set('Address',ipAddress)
                if chassisSize is not None and port.attrib['Type'] == 'PointIO':
                    for pchild in port:
                        if child.tag == 'Bus':
                            pchild.set('Size',chassisSize)

    modType = Module.objects.get(catalogNumber=catalogNumber)
    if modType.catagory is not None and  modType.catagory.catagory in ('Input','Output'):
        tree = setIoComments(tree,catalogNumber,comments)

    return tree

def setIoComments(tree,catalogNumber,comments=None):
    '''
        Set the modules comments, sent as a comma seperated string
    '''

    # comments = 'Input 0,Input 1,Input 2,Input 3'
    # print (comments)
    if comments is None:
        return tree

    module = Module.objects.get(catalogNumber=catalogNumber)
    if module.catagory.catagory == 'Input':
        type = 'InputTag'
    elif module.catagory.catagory == 'Output':
        type = 'OutputTag'
    else:
        return tree

    points = module.points
    comments = comments.split(',')
    comments = comments[:points]              # ignore items greater than the module supports

    # Drill down into the xml tree to find the comments element and add individual comments
    # as individual list items.
    for child in tree:
        if child.tag == 'Communications':
            for c1 in child:
                if c1.tag == 'Connections':
                    for c2 in c1:
                        if c2.tag == 'Connection':
                            for c3 in c2:
                                if c3.tag == type:
                                    for c4 in c3:
                                        if c4.tag == 'Comments':
                                            for i,comment in enumerate(comments):
                                                c = buildElement('Comment',{'Operand':'.DATA.' + str(i)})
                                                content = CDATA(comment)
                                                c.append(content)
                                                c4.append(c)
                                            return tree

    return tree

def getModuleChassisXML(catalogNumber,moduleName,slotNumber,ipAddress=None,parentModule='Local',chassisSize=None):
    '''
     		Get a modules xml from the db and return it after attempting to set any passed attributes
     		This is for modules like point I/O adapters that have particular chassis size related footprints.
     		Return an xml element

    '''
    # no spaces or dashes
    moduleName = moduleName.replace(' ','_')
    moduleName = moduleName.replace('-','_')

    xml = Chassis.objects.filter(catalogNumber=catalogNumber).get(size=chassisSize).xml

    print (ipAddress)

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
    				if port.attrib['Type'] == 'Ethernet' and ipAddress is not None:
    					port.set('Address',ipAddress)
    				if chassisSize is not None and port.attrib['Type'] == 'PointIO':
    					for pchild in port:
    						if pchild.tag == 'Bus':
    							pchild.set('Size',str(chassisSize))
    return tree


# def getModuleChassisXML(catalogNumber,moduleName,slotNumber,ipAddress=None,parentModule='Local',chassisSize=None):
# 	'''
# 		Get a modules xml from the db and return it after attempting to set any passed attributes
# 		This is for modules like point I/O adapters that have particular chassis size related footprints.
# 		Return an xml element
#
# 	'''
#     # no spaces or dashes
#     moduleName = moduleName.replace(' ','_')
#     moduleName = moduleName.replace('-','_')
#
#     xml = Chassis.objects.filter(catalogNumber=catalogNumber).get(size=chassisSize).xml
#
#     print (ipAddress)
#
#     if xml == '':
#     	# print 'Item ',catalogNumber,' not found!'
#     	return None
#     else:
#     	tree = ET.fromstring(xml)
#     	tree.set('Name',moduleName)
#     	if parentModule != 'Local':
#     		tree.set('ParentModule',parentModule)
#     	for child in tree:
#     		if child.tag == 'Ports':
#     			for port in child:
#     				if port.attrib['Type'] == 'ICP':
#     					port.set('Address',str(slotNumber))
#     				if port.attrib['Type'] == 'Ethernet' and ipAddress is not None:
#     					port.set('Address',ipAddress)
#     				if chassisSize is not None and port.attrib['Type'] == 'PointIO':
#     					for pchild in port:
#     						if pchild.tag == 'Bus':
#     							pchild.set('Size',str(chassisSize))
    # return tree




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
