# -*- coding: utf-8 -*-

import click

import click_utils


def test_help_env(runner):

    @click.command()
    def cli(option_a, option_b, option_c, option_d):
        click.echo(option_a)
        click.echo(option_b)
        click.echo(option_c)
        click.echo(option_d)

    option = click_utils.help.EnvHelpOption(['--option_a'], envvar='OPTIONA')
    cli.params.append(option)
    option = click_utils.help.EnvHelpOption(['--option_b'], envvar=['BVAR', 'B_VAR'])
    cli.params.append(option)
    option = click_utils.help.EnvHelpOption(['--option_c'])
    cli.params.append(option)
    option = click_utils.help.EnvHelpOption(['--option_d'], allow_from_autoenv=False)
    cli.params.append(option)

    result = runner.invoke(cli, ['--help'], catch_exceptions=False, auto_envvar_prefix='CLI')
    out = result.output
    assert '--option_a TEXT  [env: OPTIONA]' in out
    assert '--option_b TEXT  [env: BVAR, B_VAR]' in out
    assert '--option_c TEXT  [env: CLI_OPTION_C]' in out
    assert '--option_d TEXT  [env: ' not in out

    # result = runner.invoke(cli,  ['--option_a=A', '--option_b=B'], catch_exceptions=False)


def test_help_command(runner):
    @click.command(cls=click_utils.EnvHelpCommand)
    @click.option('--option_a', envvar='OPTIONA')
    @click.option('--option_b', envvar=['BVAR', 'B_VAR'])
    @click.option('--option_c', )
    @click.option('--option_d', allow_from_autoenv=False)
    def cli(option_a, option_b, option_c, option_d):
        click.echo(option_a)
        click.echo(option_b)
        click.echo(option_c)
        click.echo(option_d)

    result = runner.invoke(cli, ['--help'], catch_exceptions=False, auto_envvar_prefix='CLI')
    out = result.output
    assert '--option_a TEXT  [env: OPTIONA]' in out
    assert '--option_b TEXT  [env: BVAR, B_VAR]' in out
    assert '--option_c TEXT  [env: CLI_OPTION_C]' in out
    assert '--option_d TEXT  [env: ' not in out
