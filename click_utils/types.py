# -*- coding: utf-8 -*-

import logging

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
