import logging
import uuid

from xml.etree.ElementTree import Element, SubElement

from portfoliotool.utils.version import version_gte, version_lte
from portfoliotool.utils.xmlutils import XMLDocument


log = logging.getLogger(__name__)


def guid():
    return str(uuid.uuid4()).replace('-', '')


class RPToolsMacro(object):
    def __init__(self, c, version,
                 colorKey='default',
                 hotKey='None',
                 command=None,
                 label=None,
                 group='',
                 sortby=None,
                 autoExecute='true',
                 includeLabel='false',
                 applyToTokens='false',
                 fontColorKey='black',
                 fontSize='1.00em',
                 minWidth=None,
                 maxWidth=None,
                 allowPlayerEdits='true',
                 toolTip=None,
                 commonMacro='false',
                 compareGroup='true',
                 compareSortPrefix='true',
                 compareCommand='true',
                 compareIncludeLabel='true',
                 compareAutoExecute='true',
                 compareApplyToSelectedTokens='true'):
        assert command is not None
        assert label is not None

        self.root = Element('entry')
        SubElement(self.root, 'int').text = str(c)
        button = SubElement(self.root,
                            'net.rptools.maptool.model.MacroButtonProperties')

        if version_gte(self.version, '1.4'):
            SubElement(button, 'macroUUID').text = str(uuid.uuid4())
        SubElement(button, 'saveLocation').text = 'Token'
        SubElement(button, 'index').text = str(c)

        skip_list = ['version', 'self', 'skip_list']
        if version_lte(self.version, '1.4'):
            skip_list.append('c')
        for k, v in locals().items():
            if k in skip_list:
                continue
            if v is None:
                SubElement(button, k)
            else:
                SubElement(button, k).text = str(v)


class RPToolsToken(XMLDocument):
    _n_macros = 0
    _n_speech = 0

    propertyType = 'Basic'

    def __init__(self, character, assets, version):
        self.assets = assets
        self.character = character
        self.version = version

        self.root = Element('net.rptools.maptool.model.Token')

        SubElement(SubElement(self.root, 'id'), 'baGUID').text = guid()
        SubElement(self.root, 'beingImpersonated').text = 'false'
        SubElement(SubElement(self.root,
                              'exposedAreaGUID'), 'baGUID').text = guid()

        imageAssetMap = SubElement(self.root, 'imageAssetMap')
        entry = SubElement(imageAssetMap, 'entry')
        # this null needs to exist
        SubElement(entry, 'null')
        md5key = SubElement(entry, 'net.rptools.lib.MD5Key')
        md5id = SubElement(md5key, 'id').text = assets[0].id

        SubElement(self.root, 'x').text = '0'
        SubElement(self.root, 'y').text = '0'
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

        if version_gte(self.version, '1.4'):
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
        if version_gte(self.version, '1.4'):
            SubElement(self.root, 'vblAlphaSensitivity').text = '-1'
            SubElement(self.root, 'alwaysVisibleTolerance').text = '2'
            SubElement(self.root, 'isAlwaysVisible').text = 'false'

        SubElement(self.root, 'name').text = character.name
        SubElement(self.root, 'ownerType').text = '0'

        SubElement(self.root, 'tokenShape').text = 'SQUARE'
        SubElement(self.root, 'tokenType').text = character.role.upper()

        SubElement(self.root, 'layer').text = 'TOKEN'
        SubElement(self.root, 'propertyType').text = self.propertyType

        if version_gte(self.version, '1.4'):
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

        self.state = SubElement(self.root, 'state')
        self.props = SubElement(SubElement(self.root, 'propertyMapCI'),
                                'store')
        self.macros = SubElement(self.root, 'macroPropertiesMap')
        self.speech = SubElement(self.root, 'speechMap')
        #TODO - NERPS can support this
        # self.herolab = SubElement(self.root, 'heroLabData')

    def add_macro(self, **kwargs):
        self._n_macros += 1
        macro = RPToolsMacro(self._n_macros, self.version, **kwargs)
        self.macros.append(macro.root)

    def add_speech(self, text, id=None):
        if id is None:
            self._n_speech += 1
            id = self._n_speech
        entry = SubElement(self.speech, 'entry')
        SubElement(entry, 'string').text = str(id)
        SubElement(entry, 'string').text = text
        return id

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

    def set_state(self, key, value):
        type_map = {
            int: 'big-decimal',
            float: 'big-decimal',
            str: 'string'
            }
        type_ = type(value)
        class_ = type_map[type_] if type_ in type_map else 'string'
        entry = SubElement(self.state, 'entry')
        SubElement(entry, 'string').text = key
        SubElement(entry, class_).text = str(value)
