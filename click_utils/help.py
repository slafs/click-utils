# -*- coding: utf-8 -*-

import click


class EnvHelpOption(click.Option):
    '''
    '''

    def get_help_record(self, ctx):
        ret = super(EnvHelpOption, self).get_help_record(ctx)
        envvars = self.get_envvar_names(ctx)
        if envvars:
            prefix = ' ' if ret[1] else ''
            return ret[0], ret[1] + prefix + '[env: %s]' % ', '.join(envvars)
        return ret

    def get_envvar_names(self, ctx):
        if self.envvar is not None:
            if isinstance(self.envvar, (list, tuple)):
                return self.envvar
            else:
                return [self.envvar]
        else:
            if self.allow_from_autoenv and ctx.auto_envvar_prefix is not None:
                envvar = '%s_%s' % (ctx.auto_envvar_prefix, self.name.upper())
                return [envvar]


class EnvHelpCommand(click.Command):
    '''
    '''

    def __init__(self, *args, **kwargs):

        patch_options = kwargs.pop('envhelp_patch_options', True)
        # patch_subcommands = kwargs.pop('envhelp_patch_subcommands', False)

        super(EnvHelpCommand, self).__init__(*args, **kwargs)

        if patch_options:
            for param in self.params:
                if isinstance(param, click.Option):
                    param.__class__ = EnvHelpOption

        # if patch_subcommands:
        #     pass
