from click.testing import CliRunner

from pygent.cli import main


def test_help() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "chat" in result.output
    assert "config" in result.output


def test_version() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["--version"])

    assert result.exit_code == 0
