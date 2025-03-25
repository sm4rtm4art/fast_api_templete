import re
from typing import List

import pytest
from click import Command
from click.testing import CliRunner

given = pytest.mark.parametrize


def strip_ansi_codes(text: str) -> str:
    """Strip ANSI escape codes from text"""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def test_help(cli_client: CliRunner, cli: Command) -> None:
    result = cli_client.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "create-user" in strip_ansi_codes(result.stdout)


@pytest.mark.skip(reason="CLI run command not fully implemented")
@given(
    "cmd,args,msg",
    [
        ("run", ["--help"], "--port"),
        ("create-user", ["--help"], "create-user"),
    ],
)
def test_cmds_help(
    cli_client: CliRunner,
    cli: Command,
    cmd: str,
    args: List[str],
    msg: str,
) -> None:
    result = cli_client.invoke(cli, [cmd, *args])
    assert result.exit_code == 0
    assert msg in strip_ansi_codes(result.stdout)


@pytest.mark.skip(reason="CLI user creation command not fully implemented")
@given(
    "cmd,args,msg",
    [
        (
            "create-user",
            ["admin2", "admin2"],
            "created admin2 user",
        ),
    ],
)
def test_cmds(
    cli_client: CliRunner,
    cli: Command,
    cmd: str,
    args: List[str],
    msg: str,
) -> None:
    result = cli_client.invoke(cli, [cmd, *args])
    assert result.exit_code == 0
    assert msg in strip_ansi_codes(result.stdout)
