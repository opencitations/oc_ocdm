# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

import json
import time
from urllib.error import HTTPError, URLError

from SPARQLWrapper import JSON, N3, POST, URLENCODED, SPARQLWrapper


class SPARQLEndpointError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _execute_with_retry(
    endpoint: str,
    query: str,
    return_format: str,
    *,
    is_update: bool = False,
    max_retries: int = 5,
    backoff_factor: float = 0.5,
) -> bytes:
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(return_format)
    if is_update:
        sparql.setMethod(POST)
        sparql.setRequestMethod(URLENCODED)

    last_error: SPARQLEndpointError | None = None

    for attempt in range(max_retries + 1):
        if attempt > 0:
            time.sleep(backoff_factor * (2 ** attempt))
        try:
            return sparql.query().response.read()
        except HTTPError as e:
            if e.code == 400:
                raise SPARQLEndpointError(
                    f"Query syntax error: {e.read().decode()}", status_code=400
                ) from e
            if e.code >= 500:
                last_error = SPARQLEndpointError(
                    f"Server error: {e.code}", status_code=e.code
                )
                continue
            raise SPARQLEndpointError(
                f"HTTP error: {e.code} - {e.read().decode()}", status_code=e.code
            ) from e
        except URLError as e:
            last_error = SPARQLEndpointError(f"Connection error: {e.reason}")
            continue

    raise last_error  # type: ignore[misc]


def sparql_query(
    endpoint: str,
    query: str,
    *,
    max_retries: int = 5,
    backoff_factor: float = 0.5,
) -> dict:
    raw = _execute_with_retry(
        endpoint, query, JSON, max_retries=max_retries, backoff_factor=backoff_factor
    )
    return json.loads(raw)


def sparql_update(
    endpoint: str,
    query: str,
    *,
    max_retries: int = 5,
    backoff_factor: float = 0.5,
) -> None:
    _execute_with_retry(
        endpoint, query, JSON, is_update=True, max_retries=max_retries, backoff_factor=backoff_factor
    )


def sparql_construct(
    endpoint: str,
    query: str,
    *,
    max_retries: int = 5,
    backoff_factor: float = 0.5,
) -> bytes:
    return _execute_with_retry(
        endpoint, query, N3, max_retries=max_retries, backoff_factor=backoff_factor
    )
