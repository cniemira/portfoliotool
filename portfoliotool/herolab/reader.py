import logging
import os
import zipfile

from xml.dom import minidom

from portfoliotool.herolab.models import HeroLabPathfinderCharacter
from portfoliotool.utils.xmlutils import (
    get_attribute, get_subnode, get_subnode_subnodes
    )

character_models = {
    'Pathfinder Roleplaying Game': HeroLabPathfinderCharacter,
    }


log = logging.getLogger(__name__)


class PorReader(object):
    characters = []

    _image_files = {}
    _index_data = {}
    _file_cache = {}

    def __init__(self, por_file):
        # open the zip and create a manifest
        log.debug('Opening zipfile')
        with zipfile.ZipFile(por_file) as myzip:
            self._por_manifest = myzip.namelist()

            # cache the zip contents
            for name in self._por_manifest:
                with myzip.open(name) as myfile:
                    data = myfile.read()
                log.debug('Extracted %s (%d)' % (name, len(data)))
                self._file_cache.update({name: data})

        log.debug('Closed zipfile')

        # Open up the index.xml file, determine game type, etc...
        assert 'index.xml' in self._por_manifest
        index = minidom.parseString(self._file_cache['index.xml'])
        root = get_subnode(index, 'document')
        game = get_subnode(root, 'game')

        game_type = get_attribute(game, 'name', str)
        if game_type not in character_models:
            raise NotImplementedError(game_type)
        self.character_model = character_models[game_type]
        # TODO - version compatibility check

        # append all of the minions to the character list
        characters = get_subnode_subnodes(root, 'characters', 'character')
        for character in characters:
            try:
                characters += get_subnode_subnodes(character,
                                                   'minions',
                                                   'character')
            except UserWarning:
                pass

        # extract the characterindex => statblock mapping
        for character in characters:
            characterindex = get_attribute(character,
                                           'characterindex',
                                           int)
            summary = get_attribute(character,
                                    'summary',
                                    str)
            index_data = {'summary': summary}

            statblocks = get_subnode_subnodes(character,
                                              'statblocks',
                                              'statblock')
            for statblock in statblocks:
                file_type = get_attribute(statblock, 'format')
                file_path = os.path.join(
                            get_attribute(statblock, 'folder', str),
                            get_attribute(statblock, 'filename', str)
                            )
                index_data.update({file_type: file_path})

            image_files = []
            images = get_subnode_subnodes(character, 'images', 'image')
            for image in images:
                file_path = os.path.join(
                            get_attribute(image, 'folder', str),
                            get_attribute(image, 'filename', str)
                            )
                image_files.append(file_path)
            log.debug(image_files)
            index_data.update({'images': image_files})

            self._index_data.update({characterindex: index_data})

        # extract characters from each xml statblock
        for key, doc in self._file_cache.items():
            if not key.startswith('statblocks_xml/'):
                continue

            dom = minidom.parseString(doc)
            for character in dom.getElementsByTagName('character'):
                hlcharacter = self.character_model(character)
                data = self._index_data[hlcharacter.characterindex]
                hlcharacter.summary = data['summary']
                hlcharacter.statblock_html = self._file_cache[data['html']].decode()
                hlcharacter.statblock_text = self._file_cache[data['text']].decode()
                hlcharacter.portfolio = por_file
                for file in data['images']:
                    hlcharacter.images.append(self._file_cache[file])
                self.characters.append(hlcharacter)

                log.info('Read ' + hlcharacter.name)
