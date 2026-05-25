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


def test_layers_structure_with_database(tmp_path):
    cli = FastApiCli()
    project_dir = tmp_path / "my_project"
    cli.layers_estructure(str(project_dir), db_engine="SQLite", use_schemas=False)
    
    # Check that db.py exists
    assert (project_dir / "app" / "db.py").exists()
    
    # Check User model uses SQLModel
    user_model_file = project_dir / "app" / "models" / "user_model.py"
    assert user_model_file.exists()
    content = user_model_file.read_text()
    assert "from sqlmodel import Field, SQLModel" in content
    assert "class User(SQLModel, table=True):" in content

    # Check that main.py exists and imports the correct route
    main_file = project_dir / "app" / "main.py"
    assert main_file.exists()
    main_content = main_file.read_text()
    assert "from app.routes import user_route" in main_content
    assert "app.include_router(user_route.router)" in main_content


def test_layers_structure_without_database(tmp_path):
    cli = FastApiCli()
    project_dir = tmp_path / "my_project"
    cli.layers_estructure(str(project_dir), db_engine=None, use_schemas=False)
    
    # Check that db.py does not exist
    assert not (project_dir / "app" / "db.py").exists()
    
    # Check User model uses Pydantic BaseModel
    user_model_file = project_dir / "app" / "models" / "user_model.py"
    assert user_model_file.exists()
    content = user_model_file.read_text()
    assert "from pydantic import BaseModel" in content
    assert "class User(BaseModel):" in content

    # Check that main.py exists and imports the correct route
    main_file = project_dir / "app" / "main.py"
    assert main_file.exists()
    main_content = main_file.read_text()
    assert "from app.routes import user_route" in main_content
    assert "app.include_router(user_route.router)" in main_content


def test_generate_module_with_db(tmp_path, monkeypatch):
    cli = FastApiCli()
    project_dir = tmp_path / "my_project"
    app_dir = project_dir / "app"
    app_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock as a valid project by creating main.py and db.py
    (app_dir / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n")
    (app_dir / "db.py").write_text("pass\n")
    
    monkeypatch.chdir(project_dir)
    cli.generate_module("product")
    
    product_model_file = app_dir / "models" / "product_model.py"
    assert product_model_file.exists()
    content = product_model_file.read_text()
    assert "from sqlmodel import Field, SQLModel" in content
    assert "class Product(SQLModel, table=True):" in content


def test_generate_module_without_db(tmp_path, monkeypatch):
    cli = FastApiCli()
    project_dir = tmp_path / "my_project"
    app_dir = project_dir / "app"
    app_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock as a valid project by creating main.py but NO db.py
    (app_dir / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n")
    
    monkeypatch.chdir(project_dir)
    cli.generate_module("product")
    
    product_model_file = app_dir / "models" / "product_model.py"
    assert product_model_file.exists()
    content = product_model_file.read_text()
    assert "from pydantic import BaseModel" in content
    assert "class Product(BaseModel):" in content

