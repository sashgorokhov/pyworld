import inspect
import logging
import re

logger = logging.getLogger(__name__)


def get_var_name(frame=None):
    try:
        frame = frame or inspect.currentframe().f_back
        with open(frame.f_code.co_filename, 'r') as f:
            line = f.readlines()[frame.f_lineno - 1]
        match = re.match(r'\s*?(\S+?)\s*?=.*', line)
        if match:
            return match.group(1)
    except Exception as e:
        logger.exception('Error extracting variable name')
        logger.debug(frame)


class Signal:
    _named_signals = dict()

    def __init__(self, name=None, providing_args=None):
        name = name or get_var_name(inspect.currentframe().f_back)
        self.name = name
        self.handlers = list()

        if name is not None:
            if name in self._named_signals:
                raise KeyError('Signal with name "%s" is already defined: %s' % (name, self._named_signals[name]))
            self._named_signals[name] = self

    def __str__(self):
        return self.name or repr(self)

    def add_handler(self, func, *args, **kwargs):
        if func not in self.handlers:
            self.handlers.append(func)
            logger.debug('Added handler %s for signal %s', func, self)

    def register(self, *args, **kwargs):
        def decor(func):
            self.add_handler(func, *args, **kwargs)
            return func
        return decor

    def __call__(self, *args, **kwargs):
        return self.send(*args, **kwargs)

    def send(self, *args, suppress=False, **kwargs):
        logger.debug('Signal %s sent', self)
        results = list()

        for handler in self.handlers:
            try:
                results.append((handler, handler(*args, **kwargs)))
            except Exception as e:
                logger.exception('Error executing handler %s of signal %s', handler, self)
                if suppress:
                    results.append((handler, e))
                else:
                    raise

        return results


class AsyncSignal(Signal):
    async def send(self, *args, suppress=False, **kwargs):
        logger.debug('Signal %s sent', self)
        results = list()

        for handler in self.handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    result = await handler(*args, **kwargs)
                else:
                    result = handler(*args, **kwargs)
            except Exception as e:
                logger.exception('Error executing handler %s of signal %s', handler, self)
                if suppress:
                    result = e
                else:
                    raise
            finally:
                results.append(result)

        return results


def register(signal, *args, **kwargs):
    if isinstance(signal, str):
        signal = Signal._named_signals[signal]
    return signal.register(*args, **kwargs)
