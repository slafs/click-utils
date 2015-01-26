# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
import logging.config

import click


class LogLevelChoice(click.Choice):
    '''
    A subclass of ``click.Choice`` class for specifying a logging level.

    Example usage::

        import click
        import click_utils

        @click.command()
        @click.option('--loglevel', type=click_utils.LogLevelChoice())
        def cli(loglevel):
            click.echo(loglevel)

    This option type returns an integer representation of a logging level::

        $ cli --loglevel=error
        40

    By default available choices are the lowercased standard ``logging`` level names
    (i.e ``notset``, ``debug``, ``info``, ``warning``, ``error`` and ``critical``)::

        $ cli --help

        Usage: cli [OPTIONS]

        Options:
          --loglevel [notset|debug|info|warning|error|critical]
        ...

    But you can pass your additional logging levels like this::

        logging.addLevelName(102, 'My custom level')

        @click.command()
        @click.option('--loglevel', type=click_utils.LogLevelChoice(101, 102))
        def cli(loglevel):
            click.echo(loglevel)

        ...

        $ cli --help

        Usage: cli [OPTIONS]

        Options:
          --loglevel [notset|debug|info|warning|error|critical|level101|mycustomlevel]
        ...

        $ cli --loglevel=level101
        101

    You can also pass level name in the uppercased form::

        $ cli --loglevel=WARNING
        30

    Finally, as a special case, user can provide any integer as a logging level::

        $ cli --loglevel=123
        123

    '''

    LOGGING_LEVELS = (
        ('notset',   logging.NOTSET),
        ('debug',    logging.DEBUG),
        ('info',     logging.INFO),
        ('warning',  logging.WARNING),
        ('error',    logging.ERROR),
        ('critical', logging.CRITICAL),
    )

    @staticmethod
    def _convert_key(key):
        return key.lower().replace(' ', '')

    def __init__(self, *extra_levels):
        self.logging_levels_dict = dict(self.LOGGING_LEVELS)
        self.logging_level_keys = list(map(lambda x: x[0], self.LOGGING_LEVELS))
        for extra_level in extra_levels:
            level_name = logging.getLevelName(extra_level)
            key = self._convert_key(level_name)
            self.logging_levels_dict.update({key: extra_level})
            self.logging_level_keys.append(key)

        super(LogLevelChoice, self).__init__(self.logging_level_keys)

    def convert(self, value, param, ctx):
        lower_val = self._convert_key(value)
        if lower_val.isdigit():
            return int(lower_val)

        result = super(LogLevelChoice, self).convert(lower_val, param, ctx)
        return self.logging_levels_dict[result]


def loglevel_option(*param_decls, **attrs):
    '''Shortcut for logging level option type.

    This is equivalent to decorating a function with :func:`option` with
    the following parameters::

        @click.command()
        @click.option('--loglevel', type=click_utils.LogLevelChoice())
        def cli(loglevel):
            pass
    '''
    def decorator(f):
        attrs.setdefault('type', LogLevelChoice())
        return click.option(*(param_decls or ('--loglevel',)), **attrs)(f)
    return decorator


def logconfig_callback_factory(defaults=None, disable_existing_loggers=False):
    '''
    a factory for creating parametrized callbacks to invoke ``logging.config.fileConfig``
    '''
    def inner(ctx, param, value):
        if not value or ctx.resilient_parsing:
            return
        logging.config.fileConfig(value,
                                  defaults=defaults,
                                  disable_existing_loggers=disable_existing_loggers)
        return value
    return inner

logconfig_callback = logconfig_callback_factory()

logconfig_callback.__doc__ = '''
a default callback for invoking::

    logging.config.fileConfig(value, defaults=None, disable_existing_loggers=False)
'''


def logconfig_option(*param_decls, **attrs):
    '''An option to easily configure logging via ``logging.config.fileConfig``.
    This one allows to specify a file that will be passed as an argument
    to ``logging.config.fileConfig`` function. Using this option like this::

        @click.command()
        @click_utils.logconfig_option()
        def cli():
            pass

    is equivalent to:

    .. code-block:: python

        def mycallback(ctx, param, value):
            if not value or ctx.resilient_parsing:
                return
            logging.config.fileConfig(value,
                                      defaults=None,
                                      disable_existing_loggers=False)

        @click.command()
        @click.option('--logconfig',
                      expose_value=False,
                      type=click.Path(exists=True, file_okay=True, dir_okay=False,
                                      writable=False, readable=True, resolve_path=True)
                      callback=mycallback
                      )
        def cli():
            pass

    This option accepts all the usual arguments and keyword arguments as ``click.option``.
    Additionally it accepts two extra keyword arguments which are passed
    to ``logging.config.fileConfig``:

    * ``fileconfig_defaults`` is passed as ``defaults`` argument (default: ``None``)
    * ``disable_existing_loggers`` is passed as ``disable_existing_loggers`` argument
      (default: ``False``)

    So you can add logconfig option like this::

        @click.command()
        @click_utils.logconfig_option(disable_existing_loggers=True)
        def cli():
            pass
    '''
    def decorator(f):
        path_type = click.Path(exists=True, file_okay=True, dir_okay=False,
                               writable=False, readable=True, resolve_path=True)
        attrs.setdefault('type', path_type)
        attrs.setdefault('expose_value', False)
        disable_existing_loggers = attrs.pop('disable_existing_loggers', False)
        fileconfig_defaults = attrs.pop('fileconfig_defaults', None)

        callback_kwargs = dict(defaults=fileconfig_defaults, disable_existing_loggers=disable_existing_loggers)
        attrs.setdefault('callback', logconfig_callback_factory(**callback_kwargs))

        return click.option(*(param_decls or ('--logconfig',)), **attrs)(f)
    return decorator
