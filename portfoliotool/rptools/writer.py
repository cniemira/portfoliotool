import logging
import zipfile

from portfoliotool.rptools.models import RPToolsAsset
from portfoliotool.rptools.models import RPToolsProperties
from portfoliotool.rptools.models import RPToolsToken
from portfoliotool.utils.image import unknown_image
from portfoliotool.utils.xmlutils import html_body

log = logging.getLogger(__name__)


class RptokWriter(object):
    def __init__(self, character):
        # first assemble the properties file

        # create the assets
        self.assets = []
        if len(character.images) < 1:
            log.warn('No image found. Added a default.')
            self.assets.append(RPToolsAsset(unknown_image))

        else:
            for image in character.images:
                self.assets.append(RPToolsAsset(image))

        # dump the token contents
        self.content = RPToolsToken(character, self.assets)
        self.content.set_basic_properties()

        self.content.set_property('Description',
                                  html_body(character.statblock_html)
                                  )

        self.content.add_macro(
            label='Sheet',
            command='[frame(getName()): { [r: getProperty("Description")] }]'
            )

        self.properties = RPToolsProperties(character)

    def save_as(self, path):
        with zipfile.ZipFile(path, 'w') as myzip:
            myzip.writestr('properties.xml', str(self.properties))
            myzip.writestr('content.xml', str(self.content))
            for asset in self.assets:
                myzip.writestr(asset.xml_file, str(asset))
                myzip.writestr(asset.img_file, asset.image)
