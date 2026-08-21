import requests
from engine import SGlangEngine
from utils import process_response
import runpod
import os

# Initialize the engine
engine = SGlangEngine()
engine.start_server()
engine.wait_for_server()


def get_max_concurrency(default=300):
    """
    Returns the maximum concurrency value.

    Args:
        default (int): The default concurrency value if the environment variable is not set.

    Returns:
        int: The maximum concurrency value.
    """
    return int(os.getenv("MAX_CONCURRENCY", default))


def _error(message):
    return {"error": {"message": message, "type": "worker_error", "code": None}}


def _resolve_request(job_input):
    """Return (route, method, body) for any accepted job input shape."""
    # Case 1: full OpenAI style payload where the caller specifies the route.
    if job_input.get("openai_route"):
        body = job_input.get("openai_input")
        # The verb defaults to the payload: bodies POST, body-less requests GET,
        # so read-only routes like /v1/models work without spelling it out.
        # Pass "method" to override, e.g. to POST a deliberately empty body.
        method = (job_input.get("method") or ("POST" if body else "GET")).upper()
        return job_input["openai_route"], method, body

    # Case 2: looks like OpenAI chat/completions but omits the wrapper.
    if "messages" in job_input:
        body = dict(job_input)
        body.setdefault("model", engine.model or "default")
        return "/v1/chat/completions", "POST", body

    # Case 3: anything else goes to SGLang's native endpoint verbatim.
    return "/generate", "POST", job_input


async def async_handler(job):
    """Proxy the job to the local SGLang server."""
    job_input = job["input"]
    route, method, body = _resolve_request(job_input)
    wants_stream = isinstance(body, dict) and bool(body.get("stream", False))

    try:
        response = requests.request(
            method,
            f"{engine.base_url}{route}",
            headers={"Content-Type": "application/json"},
            json=body,
            stream=wants_stream,
        )
    except requests.RequestException as e:
        yield _error(f"Request to SGLang failed: {e}")
        return

    # Surface upstream failures instead of passing the error body off as output.
    if response.status_code >= 400:
        yield _error(f"SGLang returned HTTP {response.status_code}: {response.text}")
        return

    if wants_stream:
        for formatted_chunk in process_response(response):
            yield formatted_chunk
    else:
        # Yield the parsed object, not raw text: the platform's /openai/v1
        # passthrough returns what the handler yields, and a JSON string there
        # is not something an OpenAI client can parse.
        yield response.json()


runpod.serverless.start(
    {
        "handler": async_handler,
        "concurrency_modifier": get_max_concurrency,
        "return_aggregate_stream": True,
    }
)
