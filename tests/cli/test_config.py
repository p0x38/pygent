from pathlib import Path

import pytest
from click.testing import CliRunner

from pygent.cli import main
from pygent.config import init_config, load_config


def test_config_help() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["config", "--help"])

    assert result.exit_code == 0
    assert "get" in result.output
    assert "list" in result.output
    assert "path" in result.output


def test_config_get_missing() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["config", "get", "PYGENT_TEST_MISSING"])

    assert result.exit_code == 0
    assert "PYGENT_TEST_MISSING is not set." in result.output


def test_config_get_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYGENT_TEST_VALUE", "hello")

    runner = CliRunner()
    result = runner.invoke(main, ["config", "get", "PYGENT_TEST_VALUE"])

    assert result.exit_code == 0
    assert "PYGENT_TEST_VALUE=hello" in result.output


def test_config_get_secret_is_masked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYGENT_TEST_API_KEY", "super-secret")

    runner = CliRunner()
    result = runner.invoke(main, ["config", "get", "PYGENT_TEST_API_KEY"])

    assert result.exit_code == 0
    assert "PYGENT_TEST_API_KEY=********" in result.output
    assert "super-secret" not in result.output


def test_config_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYGENT_MODEL", "test-model")
    monkeypatch.setenv("OPENROUTER_API_KEY", "super-secret")

    runner = CliRunner()
    result = runner.invoke(main, ["config", "list"])

    assert result.exit_code == 0
    assert "Model: test-model" in result.output
    assert "API key: ********" in result.output
    assert "super-secret" not in result.output


def test_load_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        """
[default]
provider = "openrouter"
model = "test-model"
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config.default.provider == "openrouter"
    assert config.default.model == "test-model"


def test_load_config_missing(tmp_path: Path) -> None:
    config = load_config(tmp_path / "missing.toml")

    assert config.default.provider == "ollama"
    assert config.default.model == "qwen2.5-coder:3b"


def test_init_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_file = tmp_path / "pygent" / "config.toml"

    monkeypatch.setattr(
        "pygent.config.loader.config_path",
        lambda: config_file,
    )

    path = init_config()

    assert path == config_file
    assert path.exists()

    config = load_config(path)

    assert config.default.provider == "ollama"
    assert config.default.model == "qwen2.5-coder:3b"


def test_init_config_refuses_overwrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_file = tmp_path / "pygent" / "config.toml"

    monkeypatch.setattr(
        "pygent.config.loader.config_path",
        lambda: config_file,
    )

    init_config()

    with pytest.raises(FileExistsError):
        init_config()


def test_init_config_force_overwrites(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_file = tmp_path / "pygent" / "config.toml"

    monkeypatch.setattr(
        "pygent.config.loader.config_path",
        lambda: config_file,
    )

    init_config()

    config_file.write_text("invalid = true\n", encoding="utf-8")

    init_config(force=True)

    config = load_config(config_file)

    assert config.default.provider == "ollama"
    assert config.default.model == "qwen2.5-coder:3b"


def test_config_init(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_file = tmp_path / "pygent" / "config.toml"

    monkeypatch.setattr(
        "pygent.config.loader.config_path",
        lambda: config_file,
    )

    from pygent.config import init_config

    path = init_config()

    assert path == config_file
    assert path.exists()

    content = path.read_text(encoding="utf-8")

    assert "[default]" in content
    assert 'provider = "ollama"' in content
    assert 'model = "qwen2.5-coder:3b"' in content


def test_config_init_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_file = tmp_path / "pygent" / "config.toml"

    monkeypatch.setattr(
        "pygent.cli.commands.config.config_path",
        lambda: config_file,
    )

    monkeypatch.setattr(
        "pygent.cli.commands.config.init_config",
        lambda force=False: config_file,
    )

    runner = CliRunner()
    result = runner.invoke(main, ["config", "init"])

    assert result.exit_code == 0
    assert "Created configuration:" in result.output
