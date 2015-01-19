# -*- coding: utf-8 -*-

import logging
import click

import click_utils


def test_loglevel_type(runner):
    '''
    test a typical case with deafult log levels
    '''

    @click.command()
    @click.option('--loglevel', type=click_utils.LogLevelChoice())
    def cli(loglevel):
        click.echo('loglevel: {0}'.format(loglevel))

    result = runner.invoke(cli,  ['--loglevel=error'], catch_exceptions=False)

    assert result.output == 'loglevel: 40\n'

    result = runner.invoke(cli,  ['--help'])

    assert '--loglevel [notset|debug|info|warning|error|critical]' in result.output


def test_loglevel_type_extra(runner):
    '''
    test a case when a user specifies a custom logging level
    '''

    logging.addLevelName(102, 'My test level')

    @click.command()
    @click.option('--loglevel', type=click_utils.LogLevelChoice(101, 102))
    def cli(loglevel):
        click.echo('loglevel: {0}'.format(loglevel))

    result = runner.invoke(cli,  ['--help'])

    assert '--loglevel [notset|debug|info|warning|error|critical|level101|mytestlevel]' in result.output

    result = runner.invoke(cli,  ['--loglevel=mytestlevel'], catch_exceptions=False)

    assert result.output == 'loglevel: 102\n'


def test_loglevel_numeric_input(runner):
    '''
    test a special case where user inputted a number loglevel instead of a level name
    '''
    @click.command()
    @click.option('--loglevel', type=click_utils.LogLevelChoice())
    def cli(loglevel):
        assert isinstance(loglevel, int)
        click.echo('loglevel: {0}'.format(loglevel))

    result = runner.invoke(cli,  ['--loglevel=123'], catch_exceptions=False)

    assert result.output == 'loglevel: 123\n'


def test_loglevel_wrong_input(runner):
    '''
    test invokation with wrong input
    '''
    @click.command()
    @click.option('--loglevel', type=click_utils.LogLevelChoice())
    def cli(loglevel):
        click.echo('loglevel: {0}'.format(loglevel))

    result = runner.invoke(cli,  ['--loglevel=nonexistentlevel'], catch_exceptions=True)

    assert result.exit_code != 0
    assert 'Invalid value for "--loglevel": invalid choice: nonexistentlevel' in result.output
