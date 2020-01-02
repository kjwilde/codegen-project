import xml.etree.ElementTree as ET

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

def CDATA(text=None):
    
    element = ET.Element('![CDATA[')
    element.text = text
    return element

ET._original_serialize_xml = ET._serialize_xml

def _serialize_xml(write, elem, qnames, namespaces,short_empty_elements, **kwargs):

    if elem.tag == '![CDATA[':
        write("\n<{}{}]]>\n".format(elem.tag, elem.text))
        if elem.tail:
            write(_escape_cdata(elem.tail))
    else:
        return ET._original_serialize_xml(write, elem, qnames, namespaces,short_empty_elements, **kwargs)

ET._serialize_xml = ET._serialize['xml'] = _serialize_xml
