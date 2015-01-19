# encoding: utf-8

import click

import click_utils


def test_loglevel_decorator(runner):

    @click.command()
    @click_utils.loglevel_option()
    def cli(loglevel):
        assert isinstance(loglevel, int)
        click.echo(loglevel)

    result = runner.invoke(cli, ['--loglevel=error'], catch_exceptions=False)

    assert result.exit_code == 0
    assert result.output == '40\n'


def test_loglevel_decorator_custom(runner):

    @click.command()
    @click_utils.loglevel_option('--logginglevel')
    def cli(logginglevel):
        assert isinstance(logginglevel, int)
        click.echo(logginglevel)

    result = runner.invoke(cli, ['--logginglevel=info'], catch_exceptions=False)

    assert result.exit_code == 0
    assert result.output == '20\n'
