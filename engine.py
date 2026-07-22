import os
import signal
import subprocess
import time

import requests


VALUE_OPTIONS = {
    # Model / tokenizer
    "MODEL_NAME": "--model-path",
    "TOKENIZER_PATH": "--tokenizer-path",
    "TOKENIZER_MODE": "--tokenizer-mode",
    "LOAD_FORMAT": "--load-format",
    "DTYPE": "--dtype",
    "CONTEXT_LENGTH": "--context-length",
    "QUANTIZATION": "--quantization",
    "SERVED_MODEL_NAME": "--served-model-name",
    "CHAT_TEMPLATE": "--chat-template",
    "JSON_MODEL_OVERRIDE_ARGS": "--json-model-override-args",
    # Memory / scheduling
    "MEM_FRACTION_STATIC": "--mem-fraction-static",
    "MAX_RUNNING_REQUESTS": "--max-running-requests",
    "MAX_TOTAL_TOKENS": "--max-total-tokens",
    "CHUNKED_PREFILL_SIZE": "--chunked-prefill-size",
    "MAX_PREFILL_TOKENS": "--max-prefill-tokens",
    "SCHEDULE_POLICY": "--schedule-policy",
    "SCHEDULE_CONSERVATIVENESS": "--schedule-conservativeness",
    "KV_CACHE_DTYPE": "--kv-cache-dtype",
    # Parallelism
    "TENSOR_PARALLEL_SIZE": "--tp-size",
    "DATA_PARALLEL_SIZE": "--dp-size",
    "PIPELINE_PARALLEL_SIZE": "--pp-size",
    "EXPERT_PARALLEL_SIZE": "--ep-size",
    "LOAD_BALANCE_METHOD": "--load-balance-method",
    # Speculative decoding
    "SPECULATIVE_ALGORITHM": "--speculative-algorithm",
    "SPECULATIVE_DRAFT_MODEL_PATH": "--speculative-draft-model-path",
    "SPECULATIVE_NUM_STEPS": "--speculative-num-steps",
    "SPECULATIVE_EAGLE_TOPK": "--speculative-eagle-topk",
    "SPECULATIVE_NUM_DRAFT_TOKENS": "--speculative-num-draft-tokens",
    # DSA (DeepSeek Sparse Attention)
    "DSA_PREFILL_BACKEND": "--dsa-prefill-backend",
    "DSA_DECODE_BACKEND": "--dsa-decode-backend",
    # Logging / backends / misc
    "STREAM_INTERVAL": "--stream-interval",
    "RANDOM_SEED": "--random-seed",
    "LOG_LEVEL": "--log-level",
    "LOG_LEVEL_HTTP": "--log-level-http",
    "API_KEY": "--api-key",
    "FILE_STORAGE_PATH": "--file-storage-path",
    "ATTENTION_BACKEND": "--attention-backend",
    "PREFILL_ATTENTION_BACKEND": "--prefill-attention-backend",
    "DECODE_ATTENTION_BACKEND": "--decode-attention-backend",
    "SAMPLING_BACKEND": "--sampling-backend",
    "MOE_RUNNER_BACKEND": "--moe-runner-backend",
    "MOE_A2A_BACKEND": "--moe-a2a-backend",
    "CUDA_GRAPH_BACKEND_DECODE": "--cuda-graph-backend-decode",
    "CUDA_GRAPH_BACKEND_PREFILL": "--cuda-graph-backend-prefill",
    "TOOL_CALL_PARSER": "--tool-call-parser",
    "REASONING_PARSER": "--reasoning-parser",
}


BOOLEAN_OPTIONS = {
    "SKIP_TOKENIZER_INIT": "--skip-tokenizer-init",
    "TRUST_REMOTE_CODE": "--trust-remote-code",
    "LOG_REQUESTS": "--log-requests",
    "SHOW_TIME_COST": "--show-time-cost",
    "DISABLE_RADIX_CACHE": "--disable-radix-cache",
    "DISABLE_OUTLINES_DISK_CACHE": "--disable-outlines-disk-cache",
    "ENABLE_TORCH_COMPILE": "--enable-torch-compile",
    "ENABLE_P2P_CHECK": "--enable-p2p-check",
    "TRITON_ATTENTION_REDUCE_IN_FP32": "--triton-attention-reduce-in-fp32",
    "ENABLE_MIXED_CHUNK": "--enable-mixed-chunk",
    "DISABLE_OVERLAP_SCHEDULE": "--disable-overlap-schedule",
    "ENABLE_DP_ATTENTION": "--enable-dp-attention",
    "ENABLE_METRICS": "--enable-metrics",
    "ENABLE_CACHE_REPORT": "--enable-cache-report",
}


TRUE_VALUES = {"true", "1", "yes"}


class SGlangEngine:
    def __init__(self, model=None, host=None, port=None, env=None):
        self.env = os.environ if env is None else env
        self.model = model if model is not None else self.env.get("MODEL_NAME")
        self.host = host if host is not None else self.env.get("HOST", "0.0.0.0")
        port_value = port if port is not None else self.env.get("PORT", 30000)
        self.port = int(port_value)
        self.base_url = f"http://{self.host}:{self.port}"
        self.process = None

    def build_command(self):
        """Build an argv list for the SGLang v0.5.15 server."""
        command = [
            "python3",
            "-m",
            "sglang.launch_server",
            "--host",
            self.host,
            "--port",
            str(self.port),
        ]

        for env_var, option in VALUE_OPTIONS.items():
            value = self.env.get(env_var)
            if value not in (None, ""):
                command.extend([option, str(value)])

        lora_paths = self.env.get("LORA_PATHS", "")
        parsed_lora_paths = [path.strip() for path in lora_paths.split(",") if path.strip()]
        if parsed_lora_paths:
            command.append("--lora-paths")
            command.extend(parsed_lora_paths)

        for env_var, option in BOOLEAN_OPTIONS.items():
            if self.env.get(env_var, "").lower() in TRUE_VALUES:
                command.append(option)

        return command

    def start_server(self):
        command = self.build_command()
        print(f"[engine] Starting SGLang server: {' '.join(command)}")
        self.process = subprocess.Popen(command, stdout=None, stderr=None)
        print(f"[engine] Server started with PID: {self.process.pid}")

    def wait_for_server(self, timeout=900, interval=5):
        """Wait for the SGLang server to be ready, using /health first, then /v1/models."""
        start_time = time.time()
        health_url = f"{self.base_url}/health"
        models_url = f"{self.base_url}/v1/models"

        while time.time() - start_time < timeout:
            # Check if the process has crashed
            if self.process and self.process.poll() is not None:
                raise RuntimeError(
                    f"SGLang server process exited with code {self.process.returncode}"
                )

            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    print("[engine] Server is ready! (/health)")
                    return True
            except requests.RequestException:
                pass

            try:
                response = requests.get(models_url, timeout=5)
                if response.status_code == 200:
                    print("[engine] Server is ready! (/v1/models)")
                    return True
            except requests.RequestException:
                pass

            elapsed = int(time.time() - start_time)
            print(f"[engine] Waiting for server... ({elapsed}s / {timeout}s)")
            time.sleep(interval)

        raise TimeoutError("SGLang server failed to start within the timeout period.")

    def shutdown(self):
        """Graceful shutdown: SIGTERM → wait → SIGKILL."""
        if self.process:
            print("[engine] Shutting down SGLang server...")
            self.process.send_signal(signal.SIGTERM)
            try:
                self.process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                print("[engine] Server did not stop in time, sending SIGKILL...")
                self.process.kill()
                self.process.wait()
            print("[engine] Server shut down.")
