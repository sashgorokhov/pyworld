import inspect

import re


def get_var_name(frame=None):
    frame = frame or inspect.currentframe().f_back
    with open(frame.f_code.co_filename, 'r') as f:
        line = f.readlines()[frame.f_lineno - 1]
    match = re.match(r'(\S+?)\s*?=.*', line)
    if match:
        return match.group(1)


class Signal:
    _named_signals = dict()

    def __init__(self, name=None):
        name = name or get_var_name(inspect.currentframe().f_back)
        self.name = name
        self.handlers = list()

        if name is not None:
            if name in self._named_signals:
                raise KeyError('Signal with name "%s" is already defined: %s' % (name, self._named_signals[name]))
            self._named_signals[name] = self

    def add_handler(self, func, *args, **kwargs):
        if func not in self.handlers:
            self.handlers.append(func)

    def handler(self, *args, **kwargs):
        def decor(func):
            self.add_handler(func, *args, **kwargs)
            return func
        return decor

    def send(self, *args, **kwargs):
        results = list()

        for handler in self.handlers:
            try:
                results.append((handler, handler(*args, **kwargs)))
            except Exception as e:
                results.append((handler, e))

        return results


def register(signal, *args, **kwargs):
    if isinstance(signal, str):
        signal = Signal._named_signals[signal]
    return signal.handler(*args, **kwargs)

