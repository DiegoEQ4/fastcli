import pytest
from click.testing import CliRunner
from example_cli.main import group_root


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(group_root, ['--help'])
    assert result.exit_code == 0
    assert 'new' in result.output


def test_new_help():
    runner = CliRunner()
    result = runner.invoke(group_root, ['new', '--help'])
    assert result.exit_code == 0
