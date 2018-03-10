import importlib
import logging

from collections import OrderedDict, defaultdict

from portfoliotool.utils.xmlutils import (
    get_attribute, get_attributes, get_subnode, get_subnode_subnodes,
    get_textnode
    )


log = logging.getLogger(__name__)


class HeroLabPathfinderCharacter(object):
    _writers = {
        'rptok': {
            'ally': ('portfoliotool.rptools.models.pathfinder', 'AllyWriter'),
            'enemy': ('portfoliotool.rptools.models.pathfinder', 'EnemyWriter'),
            }
        }

    def __init__(self, root, game_type):
        assert root.nodeName == 'character'
        self.game_type = game_type
        self.characterindex = get_attribute(root, 'characterindex', int)

        self.images = []
        self.statblock_html = None
        self.statblock_text = None
        self.summary = None
        self.portfolio = None

        # determine if this is a minion
        if root.parentNode.nodeName == 'minions':
            self.is_minion = True
            master = root.parentNode.parentNode
            self.master_index = master.attributes['characterindex'].value

        self.name = get_attribute(root, 'name', str)
        self.playername = get_attribute(root, 'playername', str)
        self.role = get_attribute(root, 'role')
        self.relationship = get_attribute(root, 'relationship')
        self.character_type = get_attribute(root, 'type')

        space = get_subnode(root, 'size', 'space')
        self.size = get_attribute(space, 'value', int)

        health = get_subnode(root, 'health')
        self.current_hp = get_attribute(health, 'currenthp', int)
        self.max_hp = get_attribute(health, 'hitpoints', int)

        attrs = get_subnode_subnodes(root, 'attributes', 'attribute')
        self.attribute_bonuses = {}
        self.attributes = {}
        for attrnode in attrs:
            name = get_attribute(attrnode, 'name')
            attrbonus = get_subnode(attrnode, 'attrbonus')
            bonus = get_attribute(attrbonus, 'modified', int)
            self.attribute_bonuses.update({name: bonus})
            attrvalue = get_subnode(attrnode, 'attrvalue')
            value = get_attribute(attrvalue, 'modified', int)
            self.attributes.update({name: value})

        saves = get_subnode_subnodes(root, 'saves', 'save')
        self.saves = {}
        for savenode in saves:
            name = get_attribute(savenode, 'name')
            value = get_attribute(savenode, 'save', int)
            self.saves.update({name: value})

        armorclass = get_subnode(root, 'armorclass')
        self.ac = '%d %dT %dF' % (
            get_attribute(armorclass, 'ac', int),
            get_attribute(armorclass, 'touch', int),
            get_attribute(armorclass, 'flatfooted', int)
            )

        maneuvers = get_subnode(root, 'maneuvers')
        self.cmb = get_attribute(maneuvers, 'cmb', int)
        self.cmd = get_attribute(maneuvers, 'cmd', int)

        init = get_subnode(root, 'initiative')
        self.initiative = get_attribute(init, 'total', int)

        move = get_subnode(root, 'movement', 'speed')
        self.movement = get_attribute(move, 'value', int)

        skills = get_subnode_subnodes(root, 'skills', 'skill')
        self.skills = {}
        for skillnode in skills:
            name = get_attribute(skillnode, 'name')
            value = get_attribute(skillnode, 'value', int)
            self.skills.update({name: value})

        def _parse_1(nodes, name_attr='name'):
            d = {}
            for node in nodes:
                description = get_textnode(node, 'description')
                d.update({
                    get_attribute(node, name_attr, str):
                    description
                    })
            return d

        feats = get_subnode_subnodes(root, 'feats', 'feat')
        self.feats = _parse_1(feats)

        def _parse_2(nodes):
            d = {}
            for node in nodes:
                obj = get_attributes(node)
                name = obj['name']
                try:
                    description = get_textnode(node, 'description')
                    obj.update({'description': description})
                except UserWarning:
                    pass
                d.update({name: obj})
            return d

        weapons = get_subnode_subnodes(root, 'melee', 'weapon')
        self.melee = _parse_2(weapons)

        weapons = get_subnode_subnodes(root, 'ranged', 'weapon')
        self.ranged = _parse_2(weapons)

        magicitems = get_subnode_subnodes(root, 'magicitems', 'item')
        self.magicitems = _parse_1(magicitems)

        gear = get_subnode_subnodes(root, 'gear', 'item')
        self.gear = _parse_1(magicitems)

        spelllikes = get_subnode_subnodes(root, 'spelllike', 'special')
        self.spelllikes = _parse_1(spelllikes, name_attr='shortname')

        trackedresources = get_subnode_subnodes(root,
                                                'trackedresources',
                                                'trackedresource')
        self.trackedresources = _parse_2(trackedresources)

        otherspecials = get_subnode_subnodes(root,
                                             'otherspecials',
                                             'special')
        self.otherspecials = _parse_1(otherspecials, name_attr='shortname')

        def _spells_by_level(spell_dict):
            d = {}
            for name, spell in spell_dict.items():
                level = spell['level']
                if level not in d:
                    d[level] = {}
                d[level].update({name: spell})
            return d

        spellsknown = get_subnode_subnodes(root,
                                           'spellsknown',
                                           'spell')
        self.spellsknown = _parse_2(spellsknown)
        self.spellsknown_by_level = _spells_by_level(self.spellsknown)

        spellsmemorized = get_subnode_subnodes(root,
                                               'spellsmemorized',
                                               'spell')
        self.spellsmemorized = _parse_2(spellsmemorized)
        self.spellsmemorized_by_level = _spells_by_level(self.spellsmemorized)

        log.debug(self)

    def __repr__(self):
        return str(self.__dict__)

    def get_writer(self, writer_type, version):
        if writer_type not in self._writers:
            raise UserWarning(
                '{0.game_type} cannot convert to {1}'.format(
                    self, writer_type))
        writers = self._writers.get(writer_type, version)
        if self.relationship not in writers:
            raise UserWarning(
                '{0.game_type} {0.relationship} cannot convert to {1}'.format(
                    self, writer_type))
        module_name, class_name = writers.get(self.relationship)
        class_ = getattr(importlib.import_module(module_name), class_name)
        return class_(self)
