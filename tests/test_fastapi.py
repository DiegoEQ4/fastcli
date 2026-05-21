import pytest
from example_cli.fastapi import FastApiCli


def test_validate_project_method_exists():
    cli = FastApiCli()
    assert hasattr(cli, 'is_valid_project')
    assert callable(cli.is_valid_project)


def test_generate_module_no_project(tmp_path, monkeypatch):
    cli = FastApiCli()
    # Ensure we're not in a FastAPI project
    monkeypatch.chdir(tmp_path)
    # Should not raise
    cli.generate_module('items')
