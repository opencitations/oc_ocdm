# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

import glob
import os
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

import pytest

CONTAINER_NAME = "ocdm-test-qlever"
HTTP_PORT = 7019
_TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "reader")


def _wait_for_endpoint(url: str, timeout: int = 60) -> None:
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = Request(
                f"{url}?query=ASK+%7B+%3Fs+%3Fp+%3Fo+%7D",
                headers={"Accept": "application/sparql-results+json"},
            )
            urlopen(req, timeout=2)
            return
        except (URLError, OSError):
            time.sleep(1)
    raise RuntimeError(f"Endpoint {url} not ready within {timeout}s")


@pytest.fixture(scope="session", autouse=True)
def qlever_endpoint():
    subprocess.run(
        ["docker", "rm", "-f", CONTAINER_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    with tempfile.TemporaryDirectory() as data_dir:
        input_file = Path(data_dir) / "input.nt"
        with open(input_file, "w") as out:
            for nt_path in sorted(glob.glob(os.path.join(_TEST_DATA_DIR, "*.nt"))):
                with open(nt_path) as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped:
                            out.write(stripped + "\n")

        subprocess.run(
            [
                "docker", "run", "--rm",
                "--user", "root",
                "-v", f"{data_dir}:/data",
                "--entrypoint", "qlever-index",
                "adfreiburg/qlever",
                "-i", "/data/index",
                "-f", "/data/input.nt",
                "-F", "nt",
            ],
            check=True,
            capture_output=True,
        )

        subprocess.run(
            [
                "docker", "run", "-d",
                "--name", CONTAINER_NAME,
                "--user", "root",
                "-p", f"{HTTP_PORT}:7001",
                "-v", f"{data_dir}:/data",
                "--entrypoint", "qlever-server",
                "adfreiburg/qlever",
                "-i", "/data/index",
                "-j", "2",
                "-p", "7001",
                "-m", "1G",
                "-n",
            ],
            check=True,
            capture_output=True,
        )

        endpoint = f"http://localhost:{HTTP_PORT}"
        _wait_for_endpoint(endpoint)
        os.environ["SPARQL_TEST_ENDPOINT"] = endpoint
        yield endpoint

        subprocess.run(
            ["docker", "rm", "-f", CONTAINER_NAME],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
