import configparser
import logging
import os
import zipfile

import jinja2

from portfoliotool.rptools.models import RPToolsAsset
from portfoliotool.rptools.models import RPToolsProperties
from portfoliotool.rptools.models import RPToolsToken
from portfoliotool.utils.image import unknown_image
from portfoliotool.utils.jinja2 import jinja_filters
from portfoliotool.utils.xmlutils import html_body

log = logging.getLogger(__name__)


class RptokWriter(object):
    _config_path = None

    def __init__(self, character):
        self.character = character

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

        self.content.set_property('AC', self.character.ac)
        self.content.set_property('Description',
                                  html_body(character.statblock_html)
                                  )
        self.content.set_property('HP', self.character.current_hp)
        self.content.set_state('Health',
                               float(self.character.current_hp) /
                               float(self.character.max_hp))

        for attr in ['Strength', 'Dexterity', 'Constitution', 'Intelligence',
                     'Wisdom', 'Charisma']:
            if attr in self.character.attributes:
                self.content.set_property(attr,
                                          self.character.attributes[attr])

        self.properties = RPToolsProperties(character)

    def add_macros(self, config_file):
        self._config_path = os.path.dirname(os.path.abspath(config_file))
        conf = configparser.RawConfigParser()
        conf.optionxform = lambda option: option
        conf.read(config_file)
        if len(conf.sections()) < 1:
            raise UserWarning('Empty config file: ' + config_file)

        for section in conf.sections():
            if not section[0].isalpha():
                aspect = {section[1:]: self.character}
            else:
                if section.count('.') == 1:
                    scope, subscope = section.split('.', 1)
                    if not hasattr(self.character, scope):
                        raise UserWarning('Bad macro scope: ' + scope)
                    aspect = getattr(self.character, scope)
                    if subscope not in aspect:
                        continue
                    aspect = aspect[subscope]

                else:
                    if not hasattr(self.character, section):
                        raise UserWarning('Bad macro scope: ' + section)
                    aspect = getattr(self.character, section)

                if type(aspect) != dict:
                    aspect = {section: aspect}

            for key, value in aspect.items():
                macro_args = {k: v for k, v in conf.items(section)}
                for ckey, cval in macro_args.items():
                    if cval[0] in ('\'', '"'):
                        env = jinja2.Environment()
                        env.filters.update(jinja_filters)
                        tmpl = env.from_string(cval.strip('\'"'))
                    else:
                        env = jinja2.Environment(
                            loader=jinja2.FileSystemLoader(self._config_path)
                            )
                        env.filters.update(jinja_filters)
                        tmpl = env.get_template(cval)
                    rval = tmpl.render(key=key, obj=value)
                    macro_args.update({ckey: rval})
                log.info(macro_args)
                self.content.add_macro(**macro_args)

    def save_as(self, path):
        with zipfile.ZipFile(path, 'w') as myzip:
            myzip.writestr('properties.xml', str(self.properties))
            myzip.writestr('content.xml', str(self.content))
            for asset in self.assets:
                myzip.writestr(asset.xml_file, str(asset))
                myzip.writestr(asset.img_file, asset.image)
