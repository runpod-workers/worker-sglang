![SGLang worker banner](https://cpjrphpz3t5wbwfe.public.blob.vercel-storage.com/worker-sglang_banner-A9R2vQzvSUmLvqMZ8MzehfZtRDxHJR.jpeg)

Run LLMs and VLMs using [SGLang](https://docs.sglang.ai)

---

[![RunPod](https://api.runpod.io/badge/runpod-workers/worker-sglang)](https://www.runpod.io/console/hub/runpod-workers/worker-sglang)

---

## Endpoint Configuration

All behaviour is controlled through environment variables:

| Environment Variable              | Description                                       | Default                               | Options                                                                                   |
| --------------------------------- | ------------------------------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------- |
| `MODEL_NAME`                      | Hugging Face model name or local path             | "meta-llama/Meta-Llama-3-8B-Instruct" | Hugging Face repo ID or local folder path                                                 |
| `HF_TOKEN`                        | HuggingFace access token for gated/private models |                                       | Your HuggingFace access token                                                             |
| `TOKENIZER_PATH`                  | Path of the tokenizer                             |                                       |                                                                                           |
| `TOKENIZER_MODE`                  | Tokenizer mode                                    | "auto"                                | "auto", "slow"                                                                            |
| `LOAD_FORMAT`                     | Format of model weights to load                   | "auto"                                | "auto", "pt", "safetensors", "npcache", "dummy"                                           |
| `DTYPE`                           | Data type for weights and activations             | "auto"                                | "auto", "half", "float16", "bfloat16", "float", "float32"                                 |
| `CONTEXT_LENGTH`                  | Model's maximum context length                    |                                       |                                                                                           |
| `QUANTIZATION`                    | Quantization method                               |                                       | "awq", "fp8", "gptq", "marlin", "gptq_marlin", "awq_marlin", "squeezellm", "bitsandbytes" |
| `SERVED_MODEL_NAME`               | Override model name in API                        |                                       |                                                                                           |
| `CHAT_TEMPLATE`                   | Chat template name or path                        |                                       |                                                                                           |
| `MEM_FRACTION_STATIC`             | Fraction of memory for static allocation          |                                       |                                                                                           |
| `MAX_RUNNING_REQUESTS`            | Maximum number of running requests                |                                       |                                                                                           |
| `MAX_TOTAL_TOKENS`                | Maximum tokens in memory pool                     |                                       |                                                                                           |
| `CHUNKED_PREFILL_SIZE`            | Max tokens in chunk for chunked prefill           |                                       |                                                                                           |
| `MAX_PREFILL_TOKENS`              | Max tokens in prefill batch                       | 16384                                 |                                                                                           |
| `SCHEDULE_POLICY`                 | Request scheduling policy                         | "fcfs"                                | "lpm", "random", "fcfs", "dfs-weight"                                                     |
| `SCHEDULE_CONSERVATIVENESS`       | Conservativeness of schedule policy               | 1.0                                   |                                                                                           |
| `TENSOR_PARALLEL_SIZE`            | Tensor parallelism size                           | 1                                     |                                                                                           |
| `STREAM_INTERVAL`                 | Streaming interval in token length                | 1                                     |                                                                                           |
| `RANDOM_SEED`                     | Random seed                                       |                                       |                                                                                           |
| `LOG_LEVEL`                       | Logging level for all loggers                     | "info"                                |                                                                                           |
| `LOG_LEVEL_HTTP`                  | Logging level for HTTP server                     |                                       |                                                                                           |
| `API_KEY`                         | API key for the server                            |                                       |                                                                                           |
| `FILE_STORAGE_PATH`               | Directory for storing uploaded/generated files    | "sglang_storage"                      |                                                                                           |
| `DATA_PARALLEL_SIZE`              | Data parallelism size                             | 1                                     |                                                                                           |
| `LOAD_BALANCE_METHOD`             | Load balancing strategy                           | "round_robin"                         | "round_robin", "shortest_queue"                                                           |
| `SKIP_TOKENIZER_INIT`             | Skip tokenizer init                               | false                                 | boolean (true or false)                                                                   |
| `TRUST_REMOTE_CODE`               | Allow custom models from Hub                      | false                                 | boolean (true or false)                                                                   |
| `LOG_REQUESTS`                    | Log inputs and outputs of requests                | false                                 | boolean (true or false)                                                                   |
| `SHOW_TIME_COST`                  | Show time cost of custom marks                    | false                                 | boolean (true or false)                                                                   |
| `DISABLE_RADIX_CACHE`             | Disable RadixAttention for prefix caching         | false                                 | boolean (true or false)                                                                   |
| `DISABLE_CUDA_GRAPH`              | Disable CUDA Graph                                | false                                 | boolean (true or false)                                                                   |
| `DISABLE_OUTLINES_DISK_CACHE`     | Disable disk cache for Outlines grammar           | false                                 | boolean (true or false)                                                                   |
| `ENABLE_TORCH_COMPILE`            | Optimize model with torch.compile                 | false                                 | boolean (true or false)                                                                   |
| `ENABLE_P2P_CHECK`                | Enable P2P check for GPU access                   | false                                 | boolean (true or false)                                                                   |
| `ENABLE_FLASHINFER_MLA`           | Enable FlashInfer MLA optimization                | false                                 | boolean (true or false)                                                                   |
| `TRITON_ATTENTION_REDUCE_IN_FP32` | Cast Triton attention reduce op to FP32           | false                                 | boolean (true or false)                                                                   |
| `TOOL_CALL_PARSER`                | Defines the parser used to interpret responses    | qwen25                                | "llama3", "llama4", "mistral", "qwen25", "deepseekv3"                                     |

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
