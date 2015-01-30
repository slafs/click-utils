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
    test logging configuration via logconfig option
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


def test_logfile_option(runner, tmpdir):
    '''
    test a simple case with a logfile option
    '''
    tmp_file = tmpdir.mkdir('logfiles').join('test.log')
    test_logger_name = 'click_utils_test_logfile_option_loger_name'

    @click.command()
    @click_utils.logfile_option(logger_name=test_logger_name)
    def cli():
        pass

    # invoking without logfile shouldn't change anything
    runner.invoke(cli, catch_exceptions=False)
    test_logger = logging.getLogger(test_logger_name)
    assert len(test_logger.handlers) == 0

    # invoking with ``logfile`` should configure a test logger
    runner.invoke(cli,  ['--logfile={0}'.format(tmp_file.strpath)], catch_exceptions=False)
    test_logger = logging.getLogger(test_logger_name)
    assert len(test_logger.handlers) == 1
    assert isinstance(test_logger.handlers[0], logging.handlers.RotatingFileHandler)


def test_logfile_option_with_loglevel_option(runner, tmpdir):
    '''
    test logfile with loglevel and the retrieval of level from context
    '''
    tmp_file = tmpdir.mkdir('logfiles').join('test.log')
    test_logger_name = 'click_utils_test_logfile_option_with_loglevel_option_loger_name'

    @click.command()
    @click_utils.loglevel_option(expose_value=False)
    @click_utils.logfile_option(logger_name=test_logger_name)
    def cli():
        pass

    # invoking without logfile shouldn't change anything
    runner.invoke(cli, catch_exceptions=False)
    test_logger = logging.getLogger(test_logger_name)
    assert len(test_logger.handlers) == 0

    # invoking with ``logfile`` and ``loglevel`` should configure a test logger with a certain level
    runner.invoke(cli,  ['--loglevel=critical', '--logfile={0}'.format(tmp_file.strpath)], catch_exceptions=False)
    test_logger = logging.getLogger(test_logger_name)
    assert len(test_logger.handlers) == 1
    assert isinstance(test_logger.handlers[0], logging.handlers.RotatingFileHandler)

    assert test_logger.level == logging.CRITICAL


def test_logfile_option_with_storing(runner, tmpdir):
    '''
    test that storing a logger on context (from logfile_option) works
    '''
    tmp_file = tmpdir.mkdir('logfiles').join('test.log')
    tmp_file2 = tmpdir.mkdir('logfiles2').join('test2.log')
    test_logger_name = 'click_utils_test_logfile_option_with_storing_loger_name'

    @click.command()
    @click_utils.logfile_option(logger_name=test_logger_name,
                                ctx_key='logger_on_context',
                                default=tmp_file2.strpath)
    @click.pass_context
    def cli(ctx):
        assert isinstance(ctx.logger_on_context.handlers[0], logging.handlers.RotatingFileHandler)

    # invoking without logfile should configure a test logger with default file name and store it on context
    runner.invoke(cli, catch_exceptions=False)
    test_logger = logging.getLogger(test_logger_name)
    assert len(test_logger.handlers) == 1
    assert isinstance(test_logger.handlers[0], logging.handlers.RotatingFileHandler)
    assert test_logger.handlers[0].baseFilename == tmp_file2.strpath

    # invoking with ``logfile`` should configure a test logger with passed file name and store it on context
    runner.invoke(cli,  ['--logfile={0}'.format(tmp_file.strpath)], catch_exceptions=False)
    test_logger = logging.getLogger(test_logger_name)
    assert len(test_logger.handlers) == 2
    assert isinstance(test_logger.handlers[1], logging.handlers.RotatingFileHandler)
    assert test_logger.handlers[1].baseFilename == tmp_file.strpath


def test_logfile_option_with_filters(runner, tmpdir):
    '''
    test that passing an iterable of filters to logfile_option works
    '''
    tmp_file = tmpdir.mkdir('logfiles').join('test.log')
    test_logger_name = 'click_utils_test_logfile_option_with_filters_loger_name'

    class CustomFilter(logging.Filter):
        pass

    filter = CustomFilter()

    @click.command()
    @click_utils.logfile_option(logger_name=test_logger_name, filters=(filter,))
    def cli():
        pass

    runner.invoke(cli,  ['--logfile={0}'.format(tmp_file.strpath)], catch_exceptions=False)
    test_logger = logging.getLogger(test_logger_name)
    assert len(test_logger.filters) == 1

    assert isinstance(test_logger.filters[0], CustomFilter)
