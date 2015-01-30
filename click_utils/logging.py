# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
import logging.config

import click

from . import defaults


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
        lower_val = self._convert_key(value) if not isinstance(value, int) else '{0}'.format(value)
        if lower_val.isdigit():
            return int(lower_val)

        result = super(LogLevelChoice, self).convert(lower_val, param, ctx)
        return self.logging_levels_dict[result]


def loglevel_callback_factory(ctx_loglevel_attr=None):

    def inner(ctx, param, value):

        if not value or ctx.resilient_parsing:
            return
        if ctx_loglevel_attr:
            setattr(ctx, ctx_loglevel_attr, value)

        return value
    return inner


def loglevel_option(*param_decls, **attrs):
    '''Shortcut for logging level option type.

    This is equivalent to decorating a function with :func:`option` with
    the following parameters::

        @click.command()
        @click.option('--loglevel', type=click_utils.LogLevelChoice())
        def cli(loglevel):
            pass

    It also has a callback that stores a chosen loglevel on the context object.
    By default the loglevel is stored in attribute called ``click_utils_loglevel``

    To change the attribute name you can pass an keyword arg to this option
    called ``ctx_loglevel_attr``. This is useful for other options to know what
    loglevel was set. If you want to disable storing the loglevel on context
    just pass::

        @click.command()
        @click_utils.loglevel_option(ctx_loglevel_attr=False)
        def cli(loglevel):
            click.echo(loglevel)

    Also this option is eager by default.
    '''
    def decorator(f):
        ctx_loglevel_attr = attrs.pop('ctx_loglevel_attr', defaults.CONTEXT_LOGLEVEL_ATTR)
        default_callback = loglevel_callback_factory(ctx_loglevel_attr=ctx_loglevel_attr)
        attrs.setdefault('callback', default_callback)
        attrs.setdefault('is_eager', True)

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

    This option accepts all the usual arguments and keyword arguments as ``click.option``
    (be careful with passing a different ``callback`` though).
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


def logger_callback_factory(logger_name='',
                            handler_cls=None, handler_attrs=None,
                            formatter_cls=None, formatter_attrs=None,
                            filters=None,
                            level=None, ctx_loglevel_attr=None,
                            ctx_key=None):

    handler_attrs = handler_attrs if handler_attrs else {}
    formatter_attrs = formatter_attrs if formatter_attrs else {}
    filters = filters if filters else ()
    given_level = level
    ctx_loglevel_attr = ctx_loglevel_attr if ctx_loglevel_attr else defaults.CONTEXT_LOGLEVEL_ATTR

    def inner(ctx, param, value):

        if not value or ctx.resilient_parsing:
            return

        handler = handler_cls(value, **handler_attrs)

        if formatter_cls is not None:
            formatter = formatter_cls(**formatter_attrs)
            handler.setFormatter(formatter)

        level = given_level
        if level is None:
            level = getattr(ctx, ctx_loglevel_attr, defaults.LOGLEVEL)

        handler.setLevel(level)

        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)
        logger.setLevel(level)

        for filter_function in filters:
            logger.addFilter(filter_function)

        # save it in context if ``ctx_key`` was passed
        if ctx_key:
            setattr(ctx, ctx_key, logger)

        return value
    return inner


def logger_option(*param_decls, **attrs):
    '''
    An abstract option for configuring a specific handler to a given logger (root logger by default).
    This logger is then attached to a context for further usage. This option accepts
    all the

    :param handler_cls: **required** a logging Handler class. A value of this option
                        will be passed as a first positional argument while creating
                        an instance of the ``handler_cls``.

    :param handler_attrs: a dictionary of keyword arguments passed to ``handler_cls`` while instantiating
    :param formatter_cls: a Formatter class which instance will be added to a handler
    :param formatter_attrs: a dictionary of keyword arguments passed to ``formatter_cls`` while instantiating
    :param filters: an iterable of filters to add to the logger
    :param level: enforce a minimum logging level on a logger and handler. If this is ``None``
                  then a callback will try to retrieve the level from context (e.g. that was
                  stored by ``loglevel_option``). If it fails to find it a default level is ``logging.WARNING``
    :param ctx_loglevel_attr: an attribute name of the context to **find** a stored logging level
                              (by ``loglevel_option`` for example)
    :param ctx_key: an attribute name of the context to **store** a logger.
                    Pass a *falsy* value to disable storing (default: ``None``).
    :param logger_name: a name of a logger to configure (default: ``''`` i.e. a root logger)
    '''
    def decorator(f):
        callback_kwargs = {
            'handler_cls'      : attrs.pop('handler_cls'),
            'handler_attrs'    : attrs.pop('handler_attrs', {}),
            'formatter_cls'    : attrs.pop('formatter_cls', None),
            'formatter_attrs'  : attrs.pop('formatter_attrs', {}),
            'filters'          : attrs.pop('filters', None),
            'level'            : attrs.pop('level', None),
            'ctx_loglevel_attr': attrs.pop('ctx_loglevel_attr', None),
            'ctx_key'          : attrs.pop('ctx_key', None),
            'logger_name'      : attrs.pop('logger_name', ''),
        }

        default_callback = logger_callback_factory(**callback_kwargs)
        attrs.setdefault('callback', default_callback)
        attrs.setdefault('expose_value', False)
        return click.option(*(param_decls or ('--logger',)), **attrs)(f)
    return decorator


def logfile_option(*param_decls, **attrs):
    '''
    a specific type of ``logger_option`` that configures
    a logging file handler (by default it's a ``logging.handlers.RotatingFileHandler``)
    on a logger (root logger by default).

    In addition to all ``click_utils.logger_option`` and ``click.option`` arguments
    it accepts four keyword arguments to control handler creation and format settings.

    :param fmt: a format (``fmt``) argument for ``logging.Formatter`` class
    :param datefmt: a date format (``datefmt``) argument for ``logging.Formatter`` class

    :param maxBytes: a ``maxBytes`` argument for ``RotatingFileHandler`` class
    :param backupCount: a ``backupCount`` argument for ``RotatingFileHandler`` class
    '''

    def decorator(f):
        path_type = click.Path(exists=False, file_okay=True, dir_okay=False,
                               writable=True, readable=True, resolve_path=True)
        attrs.setdefault('type', path_type)

        fmt = attrs.pop('fmt', defaults.FORMAT)
        datefmt = attrs.pop('datefmt', defaults.DATEFMT)

        maxBytes = attrs.pop('maxBytes', defaults.MAXBYTES)
        backupCount = attrs.pop('backupCount', defaults.BACKUPCOUNT)

        # logger_option attrs
        attrs.setdefault('handler_cls', logging.handlers.RotatingFileHandler),
        attrs.setdefault('handler_attrs', {'maxBytes': maxBytes, 'backupCount': backupCount}),
        attrs.setdefault('formatter_cls', logging.Formatter),
        attrs.setdefault('formatter_attrs', {'fmt': fmt, 'datefmt': datefmt}),
        attrs.setdefault('filters', None),
        attrs.setdefault('level', None),
        attrs.setdefault('ctx_loglevel_attr', None),
        attrs.setdefault('ctx_key', None),
        attrs.setdefault('logger_name', ''),

        return logger_option(*(param_decls or ('--logfile',)), **attrs)(f)
    return decorator
