"""
AttrDict is useful for declarative class data mapping.
>>> class Foo(AttrDict):
...     bar = 'bar'
>>> f = Foo()
>>> f
{'bar': 'bar'}
>>> f.bar
'bar'
>>> Foo(bar='baz', foo='foo') == {'bar': 'baz', 'foo': 'foo'}
True
"""

__all__ = ['AttrDict', 'TupledAttrDict']


def parse_d(d):
    defaults = dict()
    for key in list(d.keys()):
        if key.startswith('_'):
            continue
        value = d.get(key)
        if callable(value) or isinstance(value, property) or isinstance(value, classmethod):
            continue
        defaults[key] = d.pop(key)
    return defaults


class AttrDictMeta(type):
    def __new__(mcs, name, bases, d):
        defaults = dict()
        for base in bases:
            defaults.update(getattr(base, '__defaults__', dict()))
        defaults.update(parse_d(d))
        instance = super(AttrDictMeta, mcs).__new__(mcs, name, bases, d)
        instance.__defaults__ = defaults
        return instance


class AttrDict(dict, metaclass=AttrDictMeta):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        for k, v in getattr(self, '__defaults__', dict()).items():
            if k not in self:
                self[k] = v

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self[item]

    def __getstate__(self):
        return dict(self)


class TupledAttrDict(AttrDict):
    def tuple(self):
        raise NotImplementedError

    def __iter__(self):
        yield from self.tuple()

    def __str__(self):
        return str(self.tuple())
