from unittest.mock import AsyncMock

import pytest

from app.clients.paginator import EventsPaginator


@pytest.mark.asyncio
async def test_paginator_single_page():
    client = AsyncMock()
    client.get_events.return_value = {
        "next": None,
        "previous": None,
        "results": [{"id": "1"}, {"id": "2"}],
    }

    paginator = EventsPaginator(client, changed_at="2000-01-01")
    pages = [page async for page in paginator]

    assert pages == [[{"id": "1"}, {"id": "2"}]]
    client.get_events.assert_awaited_once_with(changed_at="2000-01-01")


@pytest.mark.asyncio
async def test_paginator_multiple_pages():
    client = AsyncMock()
    client.get_events.side_effect = [
        {"next": "http://next?cursor=1", "results": [{"id": "1"}]},
        {"next": "http://next?cursor=2", "results": [{"id": "2"}]},
        {"next": None, "results": [{"id": "3"}]},
    ]

    paginator = EventsPaginator(client, changed_at="2000-01-01")
    pages = [page async for page in paginator]

    assert pages == [[{"id": "1"}], [{"id": "2"}], [{"id": "3"}]]
    assert client.get_events.await_count == 3
    assert client.get_events.await_args_list[0].kwargs == {"changed_at": "2000-01-01"}
    assert client.get_events.await_args_list[1].kwargs == {"cursor": "http://next?cursor=1"}
    assert client.get_events.await_args_list[2].kwargs == {"cursor": "http://next?cursor=2"}


@pytest.mark.asyncio
async def test_paginator_empty_results():
    client = AsyncMock()
    client.get_events.return_value = {"next": None, "results": []}

    paginator = EventsPaginator(client, changed_at="2000-01-01")
    pages = [page async for page in paginator]

    assert pages == []
    client.get_events.assert_awaited_once()
