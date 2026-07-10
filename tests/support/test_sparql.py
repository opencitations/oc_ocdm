# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

from unittest.mock import MagicMock, patch

from SPARQLWrapper import GET, POST, URLENCODED

from oc_ocdm.support.sparql import sparql_query, sparql_update


@patch("oc_ocdm.support.sparql._make_sparql_client")
def test_sparql_query_uses_get_by_default(mock_make_client: MagicMock) -> None:
    client = MagicMock()
    client.query.return_value.response.read.return_value = b'{"results":{"bindings":[]}}'
    mock_make_client.return_value = client

    result = sparql_query("http://example.org/sparql", "SELECT * WHERE { ?s ?p ?o }")

    assert result == {"results": {"bindings": []}}
    client.setMethod.assert_called_once_with(GET)
    client.setRequestMethod.assert_not_called()


@patch("oc_ocdm.support.sparql._make_sparql_client")
def test_sparql_query_uses_urlencoded_post_when_requested(mock_make_client: MagicMock) -> None:
    client = MagicMock()
    client.query.return_value.response.read.return_value = b'{"results":{"bindings":[]}}'
    mock_make_client.return_value = client

    result = sparql_query(
        "http://example.org/sparql",
        "SELECT * WHERE { ?s ?p ?o }",
        method=POST,
    )

    assert result == {"results": {"bindings": []}}
    client.setMethod.assert_called_once_with(POST)
    client.setRequestMethod.assert_called_once_with(URLENCODED)


@patch("oc_ocdm.support.sparql._make_sparql_client")
def test_sparql_update_uses_urlencoded_post(mock_make_client: MagicMock) -> None:
    client = MagicMock()
    client.query.return_value.response.read.return_value = b""
    mock_make_client.return_value = client

    result = sparql_update("http://example.org/sparql", "DELETE WHERE { ?s ?p ?o }")

    assert result is None
    client.setMethod.assert_called_once_with(POST)
    client.setRequestMethod.assert_called_once_with(URLENCODED)
