![SGLang worker banner](https://cpjrphpz3t5wbwfe.public.blob.vercel-storage.com/worker-sglang_banner-A9R2vQzvSUmLvqMZ8MzehfZtRDxHJR.jpeg)

Run LLMs and VLMs using [SGLang](https://docs.sglang.ai)

---

[![RunPod](https://api.runpod.io/badge/runpod-workers/worker-sglang)](https://www.runpod.io/console/hub/runpod-workers/worker-sglang)

---

## Hardware requirements

This worker is built on `lmsysorg/sglang:v0.5.17-cu129`.

- **The host driver must provide CUDA 12.9 or newer.** The base image declares
  `cuda>=12.9`. On an older host the container never starts: it fails in the NVIDIA
  runtime hook before the handler runs, and the worker restarts in a loop without
  being reported as unhealthy, so requests simply sit in the queue. The Hub listing
  pins `allowedCudaVersions` to `["13.0", "12.9"]` for this reason. If you deploy the
  image directly instead of from the Hub, apply the same constraint yourself.
- **Blackwell is supported.** The cu129 build ships `sm_120` kernels, so RTX PRO 6000
  Blackwell works, including the MIG slices. Verified on RTX PRO 6000 Blackwell
  Server Edition and on RTX 4090.
- The listing defaults to a wide GPU set — `ADA_24`, `AMPERE_24`, `ADA_32_PRO`,
  `ADA_48_PRO`, `AMPERE_48`, `ADA_80_PRO`, `AMPERE_80` — spanning 24GB to 80GB so the
  scheduler has somewhere to place a worker. Narrow it if you want to control cost, and
  widen it to `BLACKWELL_96` if you need a 96GB card. Note that the Blackwell MIG
  slices are not in Blackwell-named pools: `1g.24gb` sits in `AMPERE_24` and `2g.48gb`
  in `ADA_48_PRO`.

## Endpoint Configuration

All behaviour is controlled through environment variables:

| Environment Variable              | Description                                       | Default          | Options                                                                                                                                                                                                                                                                                                                                                                                         |
| --------------------------------- | ------------------------------------------------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MODEL_NAME`                      | Hugging Face model name or local path (required)  |                  | Hugging Face repo ID or local folder path                                                                                                                                                                                                                                                                                                                                                       |
| `HF_TOKEN`                        | HuggingFace access token for gated/private models |                  | Your HuggingFace access token                                                                                                                                                                                                                                                                                                                                                                   |
| `TOKENIZER_PATH`                  | Path of the tokenizer                             |                  |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `TOKENIZER_MODE`                  | Tokenizer mode                                    | "auto"           | "auto", "slow"                                                                                                                                                                                                                                                                                                                                                                                  |
| `LOAD_FORMAT`                     | Format of model weights to load                   | "auto"           | "auto", "pt", "safetensors", "npcache", "dummy"                                                                                                                                                                                                                                                                                                                                                 |
| `DTYPE`                           | Data type for weights and activations             | "auto"           | "auto", "half", "float16", "bfloat16", "float", "float32"                                                                                                                                                                                                                                                                                                                                       |
| `CONTEXT_LENGTH`                  | Model's maximum context length                    |                  |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `QUANTIZATION`                    | Quantization method                               |                  | "awq", "awq_marlin", "bitsandbytes", "compressed-tensors", "fp8", "gguf", "gptq", "gptq_marlin", "marlin", "modelopt_fp4", "modelopt_fp8", "mxfp4", "w8a8_fp8", "w8a8_int8"                                                                                                                                                                                                                     |
| `SERVED_MODEL_NAME`               | Override model name in API                        |                  |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `CHAT_TEMPLATE`                   | Chat template name or path                        |                  |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `MEM_FRACTION_STATIC`             | Fraction of memory for static allocation          |                  |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `MAX_RUNNING_REQUESTS`            | Maximum number of running requests                |                  |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `MAX_TOTAL_TOKENS`                | Maximum tokens in memory pool                     |                  |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `CHUNKED_PREFILL_SIZE`            | Max tokens in chunk for chunked prefill           |                  |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `MAX_PREFILL_TOKENS`              | Max tokens in prefill batch                       | 16384            |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `SCHEDULE_POLICY`                 | Request scheduling policy                         | "fcfs"           | "lpm", "random", "fcfs", "dfs-weight"                                                                                                                                                                                                                                                                                                                                                           |
| `SCHEDULE_CONSERVATIVENESS`       | Conservativeness of schedule policy               | 1.0              |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `TENSOR_PARALLEL_SIZE`            | Tensor parallelism size                           | 1                |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `STREAM_INTERVAL`                 | Streaming interval in token length                | 1                |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `RANDOM_SEED`                     | Random seed                                       |                  |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `LOG_LEVEL`                       | Logging level for all loggers                     | "info"           |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `LOG_LEVEL_HTTP`                  | Logging level for HTTP server                     |                  |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `API_KEY`                         | API key for the server                            |                  |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `FILE_STORAGE_PATH`               | Directory for storing uploaded/generated files    | "sglang_storage" |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `DATA_PARALLEL_SIZE`              | Data parallelism size                             | 1                |                                                                                                                                                                                                                                                                                                                                                                                                 |
| `LOAD_BALANCE_METHOD`             | Load balancing strategy                           | "round_robin"    | "round_robin", "shortest_queue"                                                                                                                                                                                                                                                                                                                                                                 |
| `SKIP_TOKENIZER_INIT`             | Skip tokenizer init                               | false            | boolean (true or false)                                                                                                                                                                                                                                                                                                                                                                         |
| `TRUST_REMOTE_CODE`               | Allow custom models from Hub                      | false            | boolean (true or false)                                                                                                                                                                                                                                                                                                                                                                         |
| `LOG_REQUESTS`                    | Log inputs and outputs of requests                | false            | boolean (true or false)                                                                                                                                                                                                                                                                                                                                                                         |
| `SHOW_TIME_COST`                  | Show time cost of custom marks                    | false            | boolean (true or false)                                                                                                                                                                                                                                                                                                                                                                         |
| `DISABLE_RADIX_CACHE`             | Disable RadixAttention for prefix caching         | false            | boolean (true or false)                                                                                                                                                                                                                                                                                                                                                                         |
| `DISABLE_CUDA_GRAPH`              | Disable CUDA Graph                                | false            | boolean (true or false)                                                                                                                                                                                                                                                                                                                                                                         |
| `DISABLE_OUTLINES_DISK_CACHE`     | Disable disk cache for Outlines grammar           | false            | boolean (true or false)                                                                                                                                                                                                                                                                                                                                                                         |
| `ENABLE_TORCH_COMPILE`            | Optimize model with torch.compile                 | false            | boolean (true or false)                                                                                                                                                                                                                                                                                                                                                                         |
| `ENABLE_P2P_CHECK`                | Enable P2P check for GPU access                   | false            | boolean (true or false)                                                                                                                                                                                                                                                                                                                                                                         |
| `TRITON_ATTENTION_REDUCE_IN_FP32` | Cast Triton attention reduce op to FP32           | false            | boolean (true or false)                                                                                                                                                                                                                                                                                                                                                                         |
| `TOOL_CALL_PARSER`                | Defines the parser used to interpret responses    |                  | "apertus2509", "cohere_command4", "deepseekv3", "deepseekv31", "deepseekv32", "deepseekv4", "gemma4", "gigachat3", "glm", "glm45", "glm47", "gpt-oss", "hermes", "hunyuan", "inkling", "interns1", "kimi_k2", "kimi_k3", "lfm2", "llama3", "mimo", "minicpm5", "minimax-m2", "minimax-m3", "mistral", "poolside_v1", "pythonic", "qwen", "qwen25", "qwen3_coder", "step3", "step3p5", "trinity" |
| `REASONING_PARSER`                | Defines the parser used for reasoning traces      |                  | "apertus2509", "cohere_command4", "deepseek-r1", "deepseek-v3", "deepseek-v4", "gemma4", "glm45", "gpt-oss", "hunyuan", "inkling", "interns1", "kimi", "kimi_k2", "kimi_k3", "mimo", "minimax", "minimax-append-think", "minimax-m3", "mistral", "nemotron_3", "poolside_v1", "qwen3", "qwen3-thinking", "step3", "step3p5"                                                                     |

## Tool/Function Calling and Reasoning

- **Tool/Function calling**: Set the `TOOL_CALL_PARSER` environment variable to match your model family. See the `TOOL_CALL_PARSER` row above for the full list of supported values. If unset, this worker does not pass `--tool-call-parser` to SGLang.

  - Example (docker-compose): add `TOOL_CALL_PARSER=llama3` under `environment:`.
  - Example (RunPod Hub): set the `TOOL_CALL_PARSER` env var in the UI.

- **Reasoning**: Set the `REASONING_PARSER` environment variable to match your model family if you want to enable reasoning traces parsing. See the `REASONING_PARSER` row above for the full list of supported values. If unset, this worker does not pass `--reasoning-parser` to SGLang.
  - Example (docker-compose): add `REASONING_PARSER=qwen3` under `environment:`.
  - Example (RunPod Hub): set the `REASONING_PARSER` env var in the UI.

## API Usage

This worker supports two API formats: **RunPod native** and **OpenAI-compatible**.

### RunPod Native API

For testing directly in the RunPod UI, use these examples in your endpoint's request tab.

#### Chat Completions

```json
{
  "input": {
    "messages": [
      { "role": "system", "content": "You are a helpful assistant." },
      { "role": "user", "content": "What is the capital of France?" }
    ],
    "max_tokens": 100,
    "temperature": 0.7
  }
}
```

#### Chat Completions (Streaming)

```json
{
  "input": {
    "messages": [
      { "role": "user", "content": "Write a short story about a robot." }
    ],
    "max_tokens": 500,
    "temperature": 0.8,
    "stream": true
  }
}
```

#### Native Text Generation

For direct SGLang text generation without OpenAI chat format:

```json
{
  "input": {
    "text": "The capital of France is",
    "sampling_params": {
      "max_new_tokens": 64,
      "temperature": 0.0
    }
  }
}
```

#### List Models

```json
{
  "input": {
    "openai_route": "/v1/models"
  }
}
```

---

### OpenAI-Compatible API

For external clients and SDKs, use the `/openai/v1` path prefix with your RunPod API key.

#### Chat Completions

**Path:** `/openai/v1/chat/completions`

```json
{
  "model": "meta-llama/Meta-Llama-3-8B-Instruct",
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user", "content": "What is the capital of France?" }
  ],
  "max_tokens": 100,
  "temperature": 0.7
}
```

#### Chat Completions (Streaming)

```json
{
  "model": "meta-llama/Meta-Llama-3-8B-Instruct",
  "messages": [
    { "role": "user", "content": "Write a short story about a robot." }
  ],
  "max_tokens": 500,
  "temperature": 0.8,
  "stream": true
}
```

#### List Models

**Path:** `/openai/v1/models`

```json
{}
```

#### Response Format

Both APIs return the same response format:

```json
{
  "choices": [
    {
      "index": 0,
      "message": { "role": "assistant", "content": "Paris." },
      "finish_reason": "stop"
    }
  ],
  "usage": { "prompt_tokens": 9, "completion_tokens": 1, "total_tokens": 10 }
}
```

---

## Usage

Below are minimal `python` snippets so you can copy-paste to get started quickly.

> Replace `<ENDPOINT_ID>` with your endpoint ID and `<API_KEY>` with a [RunPod API key](https://docs.runpod.io/get-started/api-keys).

### OpenAI compatible API

Minimal Python example using the official `openai` SDK:

```python
from openai import OpenAI
import os

# Initialize the OpenAI Client with your RunPod API Key and Endpoint URL
client = OpenAI(
    api_key=os.getenv("RUNPOD_API_KEY"),
    base_url=f"https://api.runpod.ai/v2/<ENDPOINT_ID>/openai/v1",
)
```

`Chat Completions (Non-Streaming)`

```python
response = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    messages=[{"role": "user", "content": "Give a two lines on Planet Earth ?"}],
    temperature=0,
    max_tokens=100,

)
print(f"Response: {response}")
```

`Chat Completions (Streaming)`

```python
response_stream = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    messages=[{"role": "user", "content": "Give a two lines on Planet Earth ?"}],
    temperature=0,
    max_tokens=100,
    stream=True

)
for response in response_stream:
    print(response.choices[0].delta.content or "", end="", flush=True)
```

## Compatibility

Anything not recognized by worker-sglang is forwarded verbatim to `/generate`, so advanced options in the SGLang docs (logprobs, sessions, images, etc.) also work.
