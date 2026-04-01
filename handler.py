import asyncio
import aiohttp
import json
from engine import SGlangEngine
from utils import async_process_stream
import runpod
import os

# Initialize the engine
engine = SGlangEngine()
engine.start_server()
engine.wait_for_server()

# Reusable aiohttp session (created lazily)
_session = None


async def get_session():
    global _session
    if _session is None or _session.closed:
        timeout = aiohttp.ClientTimeout(
            total=int(os.getenv("REQUEST_TIMEOUT", 600)),
            sock_read=int(os.getenv("STREAM_READ_TIMEOUT", 300)),
        )
        _session = aiohttp.ClientSession(timeout=timeout)
    return _session


def get_max_concurrency(default=300):
    """
    Returns the maximum concurrency value.
    By default, it uses 300 unless the 'MAX_CONCURRENCY' environment variable is set.
    """
    return int(os.getenv("MAX_CONCURRENCY", default))


async def async_handler(job):
    """Handle the requests asynchronously."""
    job_input = job["input"]
    session = await get_session()
    headers = {"Content-Type": "application/json"}

    # Case 1: full OpenAI style payload where caller already specifies the route.
    if job_input.get("openai_route"):
        openai_route = job_input.get("openai_route")
        openai_input = job_input.get("openai_input")
        openai_url = f"{engine.base_url}{openai_route}"

        # Support GET requests (e.g. /v1/models) when no body is provided
        if openai_input is None or openai_input == {}:
            async with session.get(openai_url) as resp:
                if resp.status == 200:
                    yield await resp.json()
                else:
                    yield {
                        "error": f"Request to {openai_route} failed with status {resp.status}",
                        "details": await resp.text(),
                    }
            return

        is_stream = openai_input.get("stream", False)

        async with session.post(
            openai_url, headers=headers, json=openai_input
        ) as resp:
            if is_stream:
                async for chunk in async_process_stream(resp):
                    yield chunk
            else:
                async for line in resp.content:
                    decoded = line.decode("utf-8").strip()
                    if decoded:
                        yield decoded

    # Case 2: payload looks like OpenAI chat/completions but omits the wrapper.
    elif "messages" in job_input:
        openai_url = f"{engine.base_url}/v1/chat/completions"

        # Make sure model is set; fall back to default.
        if "model" not in job_input:
            job_input["model"] = engine.model or "default"

        is_stream = job_input.get("stream", False)

        async with session.post(
            openai_url, headers=headers, json=job_input
        ) as resp:
            if is_stream:
                async for chunk in async_process_stream(resp):
                    yield chunk
            else:
                async for line in resp.content:
                    decoded = line.decode("utf-8").strip()
                    if decoded:
                        yield decoded

    # Case 3: payload has "prompt" → route to /v1/completions (text completions).
    elif "prompt" in job_input:
        completions_url = f"{engine.base_url}/v1/completions"

        if "model" not in job_input:
            job_input["model"] = engine.model or "default"

        is_stream = job_input.get("stream", False)

        async with session.post(
            completions_url, headers=headers, json=job_input
        ) as resp:
            if is_stream:
                async for chunk in async_process_stream(resp):
                    yield chunk
            else:
                async for line in resp.content:
                    decoded = line.decode("utf-8").strip()
                    if decoded:
                        yield decoded

    # Case 4: native /generate endpoint (requires "text", "input_ids", or "input_embeds").
    elif any(k in job_input for k in ("text", "input_ids", "input_embeds")):
        generate_url = f"{engine.base_url}/generate"

        async with session.post(
            generate_url, json=job_input, headers=headers
        ) as resp:
            if resp.status == 200:
                yield await resp.json()
            else:
                yield {
                    "error": f"Generate request failed with status code {resp.status}",
                    "details": await resp.text(),
                }

    # No recognized input format
    else:
        yield {
            "error": "Invalid input format. Provide one of: "
                     "'messages' (chat), 'prompt' (completions), "
                     "'text'/'input_ids' (generate), or 'openai_route' (raw).",
            "received_keys": list(job_input.keys()),
        }


runpod.serverless.start(
    {
        "handler": async_handler,
        "concurrency_modifier": get_max_concurrency,
        "return_aggregate_stream": True,
    }
)
