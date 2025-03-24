import re

import pytest

given = pytest.mark.parametrize


def strip_ansi_codes(text):
    """Strip ANSI escape codes from text"""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def test_help(cli_client, cli):
    result = cli_client.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "create-user" in strip_ansi_codes(result.stdout)


@given(
    "cmd,args,msg",
    [
        ("run", ["--help"], "--port"),
        ("create-user", ["--help"], "create-user"),
    ],
)
def test_cmds_help(cli_client, cli, cmd, args, msg):
    result = cli_client.invoke(cli, [cmd, *args])
    assert result.exit_code == 0
    assert msg in strip_ansi_codes(result.stdout)


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
def test_cmds(cli_client, cli, cmd, args, msg):
    result = cli_client.invoke(cli, [cmd, *args])
    assert result.exit_code == 0
    assert msg in strip_ansi_codes(result.stdout)
