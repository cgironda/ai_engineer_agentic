#!/usr/bin/env python
import os
import shutil
import subprocess
import sys
import warnings

from dev_team.crew import DevTeam

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

requirements = """
A simple account management system for a trading simulation platform.
The system should allow users to create an account, deposit funds, and withdraw funds.
The system should allow users to record that they have bought or sold shares, providing a quantity.
The system should calculate the total value of the user's portfolio, and the profit or loss from the initial deposit.
The system should be able to report the holdings of the user at any point in time.
The system should be able to report the profit or loss of the user at any point in time.
The system should be able to list the transactions that the user has made over time.
The system should prevent the user from withdrawing funds that would leave them with a negative balance, or
 from buying more shares than they can afford, or selling shares that they don't have.
The system has access to a function get_share_price(symbol) which returns the current price of a share, and includes a test implementation that returns fixed prices for AAPL, TSLA, GOOGL.
"""
module_name = "accounts.py"
class_name = "Account"

def _docker_info_ok(docker_path: str, env: dict[str, str]) -> bool:
    try:
        subprocess.run(
            [docker_path, "info"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _get_docker_context_host(docker_path: str) -> str | None:
    try:
        result = subprocess.run(
            [
                docker_path,
                "context",
                "inspect",
                "--format",
                "{{.Endpoints.docker.Host}}",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except subprocess.CalledProcessError:
        return None

    host = result.stdout.strip().strip('"')
    return host or None


def _ensure_docker_host() -> None:
    docker_path = shutil.which("docker")
    if not docker_path:
        return

    env = os.environ.copy()
    if _docker_info_ok(docker_path, env):
        if not env.get("DOCKER_HOST"):
            host = _get_docker_context_host(docker_path)
            if host:
                os.environ["DOCKER_HOST"] = host
        return

    if "DOCKER_HOST" in env:
        env.pop("DOCKER_HOST", None)
        if _docker_info_ok(docker_path, env):
            os.environ.pop("DOCKER_HOST", None)
            return

    candidates = [
        os.path.expanduser("~/.docker/run/docker.sock"),
        os.path.expanduser("~/Library/Containers/com.docker.docker/Data/docker.raw.sock"),
        os.path.expanduser("~/Library/Containers/com.docker.docker/Data/docker-cli.sock"),
    ]
    for path in candidates:
        if not os.path.exists(path):
            continue
        env = os.environ.copy()
        env["DOCKER_HOST"] = f"unix://{path}"
        if _docker_info_ok(docker_path, env):
            os.environ["DOCKER_HOST"] = env["DOCKER_HOST"]
            return

def run():
    """
    Run the crew.
    """
    _ensure_docker_host()
    inputs = {
        'requirements': requirements,  # pyright: ignore[reportUndefinedVariable]
        'module_name': module_name,  # pyright: ignore[reportUndefinedVariable]
        'class_name': class_name,  # pyright: ignore[reportUndefinedVariable]
    }

    try:
        DevTeam().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
