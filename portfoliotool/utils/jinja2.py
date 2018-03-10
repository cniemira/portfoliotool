import logging
import re

from jinja2 import evalcontextfilter, Markup, escape

log = logging.getLogger(__name__)

_crit_re = re.compile(r'(?:(?P<low>\d+)\-(?P<high>\d+)/)?×(?P<mult>\d+)')
_dice_re = re.compile(r'(?P<num>\d+)d(?P<type>\d+)(?:(?P<pos>[+\-])(?P<bonus>\d+))?')
_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


@evalcontextfilter
def nl2br(context, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', Markup('<br>\n'))
                          for p in _paragraph_re.split(escape(value)))
    if context.autoescape:
        result = Markup(result)
    return result


def fix_bonus(d):
    if d['pos'] == '-':
        d.update({'bonus': '-' + d['bonus']})
        d.pop('pos')
    return d


def from_keys(d, keys, cast=int):
    r = []
    for k in keys:
        v = 0
        if k in d and d[k] is not None:
            v = cast(d[k])
        r.append(v)
    return r


@evalcontextfilter
def parse_crit(context, value):
    log.debug('parse_crit: ' + value)
    mx = _crit_re.fullmatch(value).groupdict()
    return(from_keys(mx, ['low', 'mult']))


@evalcontextfilter
def parse_dice(context, value):
    log.debug('parse_dice: ' + value)
    mx = _dice_re.match(value).groupdict()
    mx = fix_bonus(mx)
    r = from_keys(mx, ['num', 'type', 'bonus'])
    return(r)


#    bonus = mx['bonus'] if 'bonus' in mx else 0
#    return (mx['num'], mx['type'], bonus)


jinja_filters = {
    'nl2br': nl2br,
    'parse_crit': parse_crit,
    'parse_dice': parse_dice
    }
