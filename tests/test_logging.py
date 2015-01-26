# -*- coding: utf-8 -*-

import logging
import click
import textwrap

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


def test_loglevel_decorator(runner):
    '''
    test that a shortcut decorator works
    '''
    @click.command()
    @click_utils.loglevel_option()
    def cli(loglevel):
        assert isinstance(loglevel, int)
        click.echo(loglevel)

    result = runner.invoke(cli, ['--loglevel=error'], catch_exceptions=False)

    assert result.exit_code == 0
    assert result.output == '40\n'


def test_loglevel_decorator_custom(runner):
    '''
    test that a shortcut decorator works with a different param name
    '''
    @click.command()
    @click_utils.loglevel_option('--logginglevel')
    def cli(logginglevel):
        assert isinstance(logginglevel, int)
        click.echo(logginglevel)

    result = runner.invoke(cli, ['--logginglevel=info'], catch_exceptions=False)

    assert result.exit_code == 0
    assert result.output == '20\n'


def test_loglevel_uppercase(runner):
    '''
    test invokation with uppercased level name
    '''
    @click.command()
    @click.option('--loglevel', type=click_utils.LogLevelChoice())
    def cli(loglevel):
        click.echo('loglevel: {0}'.format(loglevel))

    result = runner.invoke(cli,  ['--loglevel=WARNING'], catch_exceptions=False)

    assert result.output == 'loglevel: 30\n'


def test_logconfig_option(runner, tmpdir):
    '''
    test
    '''
    tmp_file = tmpdir.join('logging.conf')
    conf_content = textwrap.dedent('''
        [loggers]
        keys=root,clickutils_logger

        [handlers]
        keys=hand01

        [formatters]
        keys=form01

        [handler_hand01]
        class=FileHandler
        level=DEBUG
        formatter=form01
        args=('/dev/null',)

        [formatter_form01]
        format=F1 %(asctime)s %(levelname)s %(message)s
        datefmt=
        class=logging.Formatter

        [logger_clickutils_logger]
        level=CRITICAL
        handlers=hand01
        qualname=clickutils_test_logger

        [logger_root]
        handlers=hand01
    ''')

    tmp_file.write(conf_content)

    @click.command()
    @click_utils.logconfig_option()
    def cli():
        pass

    # invoking without configfile shouldn't change anything
    runner.invoke(cli, catch_exceptions=False)
    test_logger = logging.getLogger('clickutils_test_logger')
    assert len(test_logger.handlers) == 0

    # invoking with ``logconfig`` should configure loggers
    runner.invoke(cli,  ['--logconfig={0}'.format(tmp_file.strpath)], catch_exceptions=False)

    test_logger = logging.getLogger('clickutils_test_logger')

    assert len(test_logger.handlers) == 1
    assert test_logger.level == logging.CRITICAL
