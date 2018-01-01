import xml.etree.ElementTree
from xml.dom import minidom


def key(string):
    return str(string).lower().replace(' ', '_')


def get_attribute(node, attr, cast=key):
    return cast(node.attributes[attr].value)


def get_attributes(node):
    return {k: v for k, v in node.attributes.items()}


def get_subnodes(node, name):
    return list(filter(lambda x: x.nodeName == name, node.childNodes))


def get_subnode(node, *names):
    for name in names:
        subs = get_subnodes(node, name)
        if len(subs) != 1:
            raise UserWarning(name + ' count = ' + str(len(subs)))
        node = subs[0]
    return node


def get_subnode_subnodes(node, first, second):
    return get_subnodes(get_subnode(node, first), second)


def get_textnode(node, name):
    sub = get_subnode(node, name)
    return str(sub.childNodes[0].data)


def html_body(doc):
    sd = '<body>'
    ed = '</body>'
    sp = doc.find(sd) + len(sd)
    ep = doc.find(ed)
    return doc[sp:ep]


class XMLDocument(object):
    def __str__(self):
        s1 = xml.etree.ElementTree.tostring(self.root, 'ascii')
        s2 = minidom.parseString(s1)
        return s2.toprettyxml(indent='  ')
