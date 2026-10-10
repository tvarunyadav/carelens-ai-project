import asyncio
from typing import Optional
import httpx

_client: Optional[httpx.AsyncClient] = None
_client_loop: Optional[asyncio.AbstractEventLoop] = None

def get_http_client() -> httpx.AsyncClient:
    """
    Returns a shared, connection-pooled AsyncClient instance.
    Reuses TCP/TLS connections to Supabase Auth & PostgREST services,
    reducing API request latency while maintaining per-request headers.
    Uses AsyncHTTPTransport(local_address="0.0.0.0") to enforce IPv4 socket binding
    on dual-stack Windows networks without monkey-patching global socket methods.
    Automatically recreates the client if the event loop has changed or closed.
    """
    global _client, _client_loop
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if (
        _client is None
        or _client.is_closed
        or _client_loop != current_loop
        or (current_loop is not None and current_loop.is_closed())
    ):
        transport = httpx.AsyncHTTPTransport(
            local_address="0.0.0.0",
            retries=1
        )
        _client = httpx.AsyncClient(
            transport=transport,
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
            http2=False,
            trust_env=True
        )
        _client_loop = current_loop
    return _client

async def close_http_client() -> None:
    """
    Closes the shared HTTP client gracefully during application shutdown.
    """
    global _client, _client_loop
    if _client is not None and not _client.is_closed:
        await _client.aclose()
        _client = None
        _client_loop = None
