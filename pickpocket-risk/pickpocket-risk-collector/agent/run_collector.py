"""Command-line entry point that runs the pickpocket report collector tool."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import Any
from urllib.parse import urlparse, urlunparse

from fastmcp.client import Client

DEFAULT_TRANSPORT = "http://127.0.0.1:8000/mcp"
TOOL_NAME = "collect_pickpocket_reports"


def _normalize_transport(value: str) -> str:
    """Ensure HTTP transports include the default /mcp path."""
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"} and parsed.path in {"", "/"}:
        parsed = parsed._replace(path="/mcp")
        return urlunparse(parsed)
    return value


async def _run_collection_task(
    transport: str,
    query: str | None,
    max_results: int,
) -> None:
    async with Client(transport) as client:
        tools = await client.list_tools()
        tool_names = [tool.name for tool in tools]
        if TOOL_NAME not in tool_names:
            available = ", ".join(sorted(tool_names))
            raise RuntimeError(
                f"Tool '{TOOL_NAME}' not registered. Available tools: {available or 'none'}"
            )

        arguments: dict[str, object] = {"max_results": max_results}
        if query:
            arguments["query"] = query

        result = await client.call_tool(TOOL_NAME, arguments=arguments)
        payload: dict[str, Any] | None = None
        if result.structured_content and isinstance(result.structured_content, dict):
            payload = result.structured_content
        elif isinstance(result.data, dict):
            payload = result.data

        if payload is not None:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(result.content)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Collect recent pickpocket incident reports using the FastMCP server "
            "and persist them to the local dataset."
        )
    )
    parser.add_argument(
        "--query",
        help="Additional keywords or location filters to refine the pickpocket search.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=15,
        help="Maximum number of reports to keep from the feed (1-25).",
    )
    parser.add_argument(
        "--server",
        default=DEFAULT_TRANSPORT,
        help=(
            "FastMCP transport to connect to (URL, socket path, or module reference). "
            f"Default: {DEFAULT_TRANSPORT}"
        ),
    )
    args = parser.parse_args()

    if args.max_results < 1 or args.max_results > 25:
        parser.error("--max-results must be between 1 and 25.")

    transport = _normalize_transport(args.server)
    try:
        asyncio.run(_run_collection_task(transport, args.query, args.max_results))
    except RuntimeError as exc:
        print(
            f"Failed to connect to FastMCP server via '{transport}': {exc}",
            file=sys.stderr,
        )
        print(
            "Ensure the server is running (e.g., "
            "`fastmcp run --transport http mcp_server/server.py:app`).",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
