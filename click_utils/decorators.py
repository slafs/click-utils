# encoding: utf-8

import click

from . import LogLevelChoice


def loglevel_option(*param_decls, **attrs):
    """Shortcut for logging level option type.

    This is equivalent to decorating a function with :func:`option` with
    the following parameters::

        @click.command()
        @click.option('--loglevel', type=click_utils.LogLevelChoice())
        def cli(loglevel):
            pass
    """
    def decorator(f):
        attrs.setdefault('type', LogLevelChoice())
        return click.option(*(param_decls or ('--loglevel',)), **attrs)(f)
    return decorator
