# overview:
# main sets up a sglang server, waits for it ("sglang") to begin serving, and then starts a serverless worker that listens for http requests with JSON bodies.
# it decodes those bodies and sends them to our 'handler' function.
# handler translates the request into a sglang request, sends it to sglang, and then sends the response back to the client, doing some
# light formatting along the way.
from os import path
from typing import Any
from typing import AsyncIterable
import json
import os
import requests
import runpod
import subprocess
import sys
import time

# TODO: add link to final documentation
modelcache_docs_link = (
    "<DRAFT GUIDE>: https://gist.github.com/ef0xa/70ec948ed9e997ef39412471636e5a58"
)
HOST, PORT = "0.0.0.0", 30000


def find_cached_model(dir: str = "/runpod/cache/model") -> str | None:
    """,
    Look for a model from the runpod huggingface model cache. TODO: add link to final documentation

    Resolution order:
     - the first value in the RUNPOD_HUGGINGFACE_MODEL environment variable
     - or the first directory three levels down from base_dir (i.e, basedir/user/model/revision)
     - or None
    See the draft developer guide here: "<DRAFT GUIDE>: https://gist.github.com/ef0xa/70ec948ed9e997ef39412471636e5a58"
    """
    dir = os.path.abspath(dir)
    print(f"runpod: looking for model in {dir}", file=sys.stderr)

    raw: str = os.environ.get("RUNPOD_HUGGINGFACE_MODEL", "")
    if (
        raw != ""
    ):  # in form of "user/model:revision", leading to "basedir/user/model/revision"

        if ":" in raw:  # user/model:revision
            longmodel, revision = raw.rsplit(":", maxsplit=1)
        else:  # user/model: default revision "main"
            longmodel, revision = raw, "main"
        if "/" not in longmodel:
            raise ValueError(
                f"invalid model: expected one in the form user/model[:path], but got {longmodel}"
            )
        os.environ["MODEL_NAME"] = (
            longmodel  # unsure if this is necessary; the dockerfile uses these environment variable but IDK if it's just cargo culting
        )
        os.environ["MODEL_REVISION"] = revision  # see above
        user, model = longmodel.rsplit("/", maxsplit=1)

        return os.path.join(dir, user, longmodel, revision)

    # just pick the first one we find that's three levels down; i.e,    basedir/user/model/revision

    subdirs = (
        path.join(dir, d) for d in os.listdir(dir) if path.isdir(path.join(dir, d))
    )  # 1
    subsubdirs = (
        path.join(d, sd)
        for d in subdirs
        for sd in os.listdir(d)
        if path.isdir(path.join(d, sd))
    )  # 2
    for subdir in subsubdirs:  # 3 : now get the first one
        return subdir
    return None


def format_server_sent_event_chunk(chunk: str):
    """format the response as a SSE-style chunk https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#event_stream_format
    for compatibility OpenAI's streaming API."""
    chunk = chunk.strip()
    if chunk.startswith("data: "):
        chunk = chunk[6:]  # Remove 'data: ' prefix

    if chunk == "[DONE]":
        return f"data: {chunk}\n\n"

    try:
        # Try to parse as JSON
        data = json.loads(chunk)
        formatted_json = json.dumps(data, indent=4)
        formatted_lines = [f"data: {line}" for line in formatted_json.split("\n")]
        return "\n".join(formatted_lines) + "\n\n"
    except json.JSONDecodeError:
        # If it's not valid JSON, return as plain text
        return f"data: {chunk}\n\n"


async def _handler(input: dict[str, Any]) -> AsyncIterable[Any]:
    """accept a job and hand it off to the sglang server located at `sglang_url`"""
    url = f"http://{HOST}:{PORT}/v1/"
    if input.get("openai_route"):
        openai_route, openai_input = input.get("openai_route", ""), input.get(
            "openai_input", ""
        )
        response = requests.post(
            f"{url}/{openai_route}",
            headers={"Content-Type": "application/json"},
            json=openai_input,
        )
        # Process the streamed response
        if openai_input.get("stream", False):
            line: bytes
            for line in response.iter_lines():
                try:
                    formatted = format_server_sent_event_chunk(line.decode("utf-8"))
                except Exception as e:
                    formatted = f"data: bad decode:{line.decode("utf-8")!r}\n\n"
                yield formatted
            return

        for chunk in response.iter_lines():
            if chunk:
                decoded_chunk = chunk.decode("utf-8")
                yield decoded_chunk
        return

    # Directly pass `job_input` to `json`. Can we tell users the possible fields of `job_input`?
    response = requests.post(
        f"{url}/generate", json=input, headers={"Content-Type": "application/json"}
    )
    if response.status_code == 200:
        yield response.json()
    else:
        yield {
            "error": f"Generate request failed with status code {response.status_code}",
            "details": response.text,
        }


def start_server(
    model_path: str | None = None, host="0.0.0.0", port=30000, wait=True
) -> subprocess.Popen:
    """
    start the sglang server, serving the model at `model_path` on `host` and `port`,
    and wait for it to be ready before returning the process object.
    """

    # convert environment variables to command line flags as necessary

    flags: dict[str, str] = {}
    for env_var, option in {  # mapping of environment variables to command line flags
        "ADDITIONAL_PORTS": "--additional-ports",
        "API_KEY": "--api-key",
        "CHAT_TEMPLATE": "--chat-template",
        "CHUNKED_PREFILL_SIZE": "--chunked-prefill-size",
        "CONTEXT_LENGTH": "--context-length",
        "DATA_PARALLEL_SIZE": "--data-parallel-size",
        "DTYPE": "--dtype",
        "FILE_STORAGE_PTH": "--file-storage-pth",
        "HOST": "--host",
        "LOAD_BALANCE_METHOD": "--load-balance-method",
        "LOAD_FORMAT": "--load-format",
        "LOG_LEVEL_HTTP": "--log-level-http",
        "LOG_LEVEL": "--log-level",
        "MAX_NUM_REQS": "--max-num-reqs",
        "MAX_PREFILL_TOKENS": "--max-prefill-tokens",
        "MAX_RUNNING_REQUESTS": "--max-running-requests",
        "MAX_TOTAL_TOKENS": "--max-total-tokens",
        "MEM_FRACTION_STATIC": "--mem-fraction-static",
        "MODEL_NAME": "--model-path",
        "PORT": "--port",
        "QUANTIZATION": "--quantization",
        "RANDOM_SEED": "--random-seed",
        "SCHEDULE_CONSERVATIVENESS": "--schedule-conservativeness",
        "SCHEDULE_POLICY": "--schedule-policy",
        "SERVED_MODEL_NAME": "--served-model-name",
        "STREAM_INTERVAL": "--stream-interval",
        "TENSOR_PARALLEL_SIZE": "--tensor-parallel-size",
        "TOKENIZER_MODE": "--tokenizer-mode",
        "TOKENIZER_PATH": "--tokenizer-path",
    }.items():
        if os.getenv(env_var):
            flags[option] = os.getenv(env_var, "")

    bools = []
    for k in [
        "SKIP_TOKENIZER_INIT",
        "TRUST_REMOTE_CODE",
        "LOG_REQUESTS",
        "SHOW_TIME_COST",
        "DISABLE_FLASHINFER",
        "DISABLE_FLASHINFER_SAMPLING",
        "DISABLE_RADIX_CACHE",
        "DISABLE_REGEX_JUMP_FORWARD",
        "DISABLE_CUDA_GRAPH",
        "DISABLE_DISK_CACHE",
        "ENABLE_TORCH_COMPILE",
        "ENABLE_P2P_CHECK",
        "ENABLE_MLA",
        "ATTENTION_REDUCE_IN_FP32",
        "EFFICIENT_WEIGHT_LOAD",
    ]:
        if os.getenv(k, "").lower() in ["true", "1", "yes"]:
            bools.append(f"--{k.lower().replace('_', '-')}")

    # overwrite environment-provided flags with our runpod-specific overrides
    # model (using cached model instead)
    # host and port (always default: we control where the server runs)

    if model_path:  # overwrite the environment variable
        flags["model_path"] = model_path
    flags["host"] = host
    flags["port"] = port

    command = (
        [
            "python3",
            "-m",
            "sglang.launch_server",
        ]
        + [f"{k}={flags[k]}" for k in flags]
        + sorted(bools)
    )

    process = subprocess.Popen(command)

    print("started server - waiting for up to 120s for it to be ready")
    start_time = time.time()
    while (remaining := 120 - (time.time() - start_time)) > 0:
        try:
            response = requests.get(f"http://{host}:{port}/v1/models")
            if response.status_code == 200:
                print(f"server ready after {time.time() - start_time:.2f}s")
                return process
            else:
                print(f"server not ready yet: {response.status_code}")
        except requests.RequestException:
            continue
        time.sleep(0.1)  # sleep for 100ms
        if time.time() - start_time > 120:
            raise TimeoutError("Server failed to start within the timeout period.")
    return process


def main():
    model = find_cached_model()
    if model is None and os.getenv("RUNPOD_HUGGINGFACE_MODEL") is None:
        raise KeyError(
            f"""Could not find a cached model. You do not have a RUNPOD_HUGGINGFACE_MODEL environment variable set. This is probably a configuration error. See the documentation at {modelcache_docs_link} for more information."""
        )
    elif model is None:
        raise FileNotFoundError(
            f"""Could not find a cached model. Your RUNPOD_HUGGINGFACE_MODEL environment variable is set to {os.getenv("RUNPOD_HUGGINGFACE_MODEL")}, but this model does not exist in the cache. This is probably a configuration error,
See the documentation at {modelcache_docs_link} for more information.
If that doesn't help, please contact support with the contents of this error message and the following information:
- Link to your model page on Hugging Face
- Your pod ID
"""
        )

    print(f"found cached model at {model}", file=sys.stderr)
    print(f"starting server at {HOST}:{PORT}", file=sys.stderr)
    with start_server(model_path=model, host=HOST, port=PORT) as server:
        print("sglang server started at http://{HOST}:{PORT}", file=sys.stderr)
        runpod.serverless.start(
            {
                "concurrency_modifier": int(os.getenv("MAX_CONCURRENCY", "300")),
                "handler": lambda job: _handler(job, HOST, PORT),
                "return_aggregate_stream": True,
            }
        )


if __name__ == "__main__":
    main()
