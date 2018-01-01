import logging
import uuid

from xml.etree.ElementTree import Element, SubElement

from portfoliotool.utils.xmlutils import XMLDocument
from portfoliotool.rptools.models.data import basic_properties


log = logging.getLogger(__name__)


def guid():
    return str(uuid.uuid4()).replace('-', '')


class RPToolsMacro(object):
    def __init__(self, c, label='', command=''):
        self.root = Element('entry')
        SubElement(self.root, 'int').text = str(c)
        button = SubElement(self.root,
                            'net.rptools.maptool.model.MacroButtonProperties')
        SubElement(button, 'macroUUID').text = str(uuid.uuid4())
        SubElement(button, 'saveLocation').text = 'Token'
        SubElement(button, 'index').text = '1'
        SubElement(button, 'colorKey').text = 'default'
        SubElement(button, 'hotKey').text = 'None'
        SubElement(button, 'command').text = command
        SubElement(button, 'label').text = label
        SubElement(button, 'group').text = 'my_group'
        SubElement(button, 'sortby')
        SubElement(button, 'autoExecute').text = 'true'
        SubElement(button, 'includeLabel').text = 'false'
        SubElement(button, 'applyToTokens').text = 'false'
        SubElement(button, 'fontColorKey').text = 'black'
        SubElement(button, 'fontSize').text = '1.00em'
        SubElement(button, 'minWidth')
        SubElement(button, 'maxWidth')
        SubElement(button, 'allowPlayerEdits').text = 'true'
        SubElement(button, 'toolTip')
        SubElement(button, 'commonMacro').text = 'false'
        SubElement(button, 'compareGroup').text = 'true'
        SubElement(button, 'compareSortPrefix').text = 'true'
        SubElement(button, 'compareCommand').text = 'true'
        SubElement(button, 'compareIncludeLabel').text = 'true'
        SubElement(button, 'compareAutoExecute').text = 'true'
        SubElement(button, 'compareApplyToSelectedTokens').text = 'true'


class RPToolsToken(XMLDocument):
    _n_macros = 0

    def __init__(self, character, assets):
        self.assets = assets
        self.character = character

        self.root = Element('net.rptools.maptool.model.Token')

        SubElement(SubElement(self.root, 'id'), 'baGUID').text = guid()
        SubElement(self.root, 'beingImpersonated').text = 'false'
        SubElement(SubElement(self.root,
                              'exposedAreaGUID'), 'baGUID').text = guid()

        imageAssetMap = SubElement(self.root, 'imageAssetMap')
        # for asset in assets:
        entry = SubElement(imageAssetMap, 'entry')
        # this null needs to exist
        SubElement(entry, 'null')
        md5key = SubElement(entry, 'net.rptools.lib.MD5Key')
        md5id = SubElement(md5key, 'id').text = assets[0].id

        SubElement(self.root, 'x').text = '1000'
        SubElement(self.root, 'y').text = '250'
        SubElement(self.root, 'z').text = '1'
        SubElement(self.root, 'anchorX').text = '0'
        SubElement(self.root, 'anchorY').text = '0'
        SubElement(self.root, 'sizeScale').text = '1.0'
        SubElement(self.root, 'lastX').text = '0'
        SubElement(self.root, 'lastY').text = '0'
        SubElement(self.root, 'snapToScale').text = 'true'

        height, width = assets[0].image_size
        SubElement(self.root, 'width').text = str(width)
        SubElement(self.root, 'height').text = str(height)

        SubElement(self.root, 'isoWidth').text = '0'
        SubElement(self.root, 'isoHeight').text = '0'
        SubElement(self.root, 'scaleX').text = '1.0'
        SubElement(self.root, 'scaleY').text = '1.0'

        entry = SubElement(SubElement(self.root, 'sizeMap'), 'entry')
        SubElement(entry, 'java-class').text = \
            'net.rptools.maptool.model.SquareGrid'
        SubElement(
            SubElement(entry, 'net.rptools.maptool.model.GUID'),
            'baGUID'
            ).text = 'fwABAc9lFSoFAAAAKgABAQ=='

        SubElement(self.root, 'snapToGrid').text = 'true'
        SubElement(self.root, 'isVisible').text = 'true'
        SubElement(self.root, 'visibleOnlyToOwner').text = 'false'
        SubElement(self.root, 'vblAlphaSensitivity').text = '-1'
        SubElement(self.root, 'alwaysVisibleTolerance').text = '2'
        SubElement(self.root, 'isAlwaysVisible').text = 'false'

        SubElement(self.root, 'name').text = character.name
        SubElement(self.root, 'ownerType').text = '0'

        SubElement(self.root, 'tokenShape').text = 'SQUARE'
        SubElement(self.root, 'tokenType').text = character.role.upper()

        SubElement(self.root, 'layer').text = 'TOKEN'
        # TODO - Use custom properties
        SubElement(self.root, 'propertyType').text = 'Basic'

        SubElement(self.root, 'tokenOpacity').text = '1.0'
        SubElement(self.root, 'isFlippedX').text = 'false'
        SubElement(self.root, 'isFlippedY').text = 'false'

        if len(assets) > 1:
            id = SubElement(SubElement(self.root, 'portraitImage'), 'id')
            id.text = assets[1].id
        else:
            SubElement(self.root, 'portraitImage',
                       {'reference':
                        '../imageAssetMap/entry/net.rptools.lib.MD5Key'})

        SubElement(self.root, 'hasSight').text = 'false'

        SubElement(self.root, 'notes').text = character.statblock_text
        SubElement(self.root, 'gmNotes')
        SubElement(self.root, 'gmName').text = character.summary
        SubElement(self.root, 'state')

        self.props = SubElement(SubElement(self.root, 'propertyMapCI'),
                                'store')
        self.macros = SubElement(self.root, 'macroPropertiesMap')
        self.speech = SubElement(self.root, 'speechMap')
        # self.herolab = SubElement(self.root, 'heroLabData')

    def add_macro(self, **kwargs):
        self._n_macros += 1
        macro = RPToolsMacro(self._n_macros, **kwargs)
        self.macros.append(macro.root)

    def set_basic_properties(self):
        for prop in basic_properties:
            if not hasattr(self.character, prop):
                continue
            value = getattr(self.character, prop)
            self.set_property(prop, value)

    def set_property(self, key, value):
        # type_ = 'int' if type(value) is int else 'string'
        type_ = 'string'
        entry = SubElement(self.props, 'entry')
        SubElement(entry, 'string').text = key
        kv = SubElement(entry,
                        'net.rptools.CaseInsensitiveHashMap_-KeyValue')
        SubElement(kv, 'key').text = key
        SubElement(kv, 'value', {'class': type_}).text = str(value)
        SubElement(kv, 'outer-class', {'reference': '../../../..'})
