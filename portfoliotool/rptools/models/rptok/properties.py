from xml.etree.ElementTree import Element, SubElement

from portfoliotool.utils.xmlutils import XMLDocument


class RPToolsProperties(XMLDocument):
    def __init__(self, image, version):
        self.root = Element('map')
        entry = SubElement(self.root, 'entry')
        SubElement(entry, 'string').text = 'version'
        SubElement(entry, 'string').text = version

        entry = SubElement(self.root, 'entry')
        SubElement(entry, 'string').text = 'herolab'
        SubElement(entry, 'string').text = 'false'
