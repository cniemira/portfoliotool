import hashlib
import imghdr
import logging
import os

from xml.etree.ElementTree import Element, SubElement

from portfoliotool.utils.image import get_image_size
from portfoliotool.utils.xmlutils import XMLDocument

log = logging.getLogger(__name__)


class RPToolsAsset(XMLDocument):
    def __init__(self, image, version):
        self.image = image

        self.image_type = imghdr.what(None, h=image)
        if self.image_type not in ('gif', 'jpeg', 'png'):
            raise UserWarning('Assets must be gif, jpg or png.')

        self.image_size = get_image_size(image)
        log.debug(self.image_size)

        md5 = hashlib.new('md5')
        md5.update(image)
        self.id = md5.hexdigest()

        self.xml_file = os.path.join('assets', self.id)
        self.img_file = self.xml_file + '.' + self.image_type

        self.root = Element('net.rptools.maptool.model.Asset')
        SubElement(SubElement(self.root, 'id'), 'id').text = self.id
        SubElement(self.root, 'name').text = 'None'
        SubElement(self.root, 'extension').text = self.image_type
        SubElement(self.root, 'image')
