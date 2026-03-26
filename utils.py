import json


def format_sse_chunk(chunk: str) -> str:
    """Format a single SSE chunk for streaming responses."""
    chunk = chunk.strip()

    # Strip existing "data: " prefix if present
    if chunk.startswith("data: "):
        chunk = chunk[6:]

    if chunk == "[DONE]":
        return "data: [DONE]\n\n"

    try:
        # Validate JSON and re-serialize compactly (no pretty-print for perf)
        data = json.loads(chunk)
        return f"data: {json.dumps(data)}\n\n"
    except json.JSONDecodeError:
        return f"data: {chunk}\n\n"


async def async_process_stream(response):
    """Process an aiohttp streaming response, yielding formatted SSE chunks."""
    async for raw_line in response.content:
        line = raw_line.decode("utf-8").strip()
        if line:
            yield format_sse_chunk(line)
