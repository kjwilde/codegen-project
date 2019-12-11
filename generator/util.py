def parseAutoGenImport(inputFile,parseType='Slot',startLine=8):
    '''
        inputFile is a request.FILE objects
        parseType is the thing we're parsing for e.g. Slot, Point, etc.
        startLine is the first line to begin dataset (has headsers)
        return a dataset with the headers at row 0
    '''

    fileData = inputFile.read().decode('utf-8')
    lines = fileData.split('\r\n')
    hdrs = lines[startLine].split(',')
    dataLines = []
    for i in range(startLine + 1,len(lines)):
        dataLines.append(lines[i].split(','))
    # extract data from the columns we're interested in
    retLines = [x for x in dataLines if len(x[hdrs.index(parseType)]) > 0]
    retLines.insert(0,hdrs)
    return retLines


def prettify(elem):
	'''
		Makes an xml file pretty for printing
		and returns it.

	'''
	from xml.dom import minidom
	import xml.etree.ElementTree as ET

	rough_string = ET.tostring(elem, 'utf-8')
	reparsed = minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="  ")
