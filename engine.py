import subprocess
import signal
import time
import requests
import os


class SGlangEngine:
    def __init__(
        self,
        model=os.getenv("MODEL_NAME"),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 30000)),
    ):
        self.model = model
        self.host = host
        self.port = port
        self.base_url = f"http://{self.host}:{self.port}"
        self.process = None

    def start_server(self):
        command = [
            "python3",
            "-m",
            "sglang.launch_server",
            "--host",
            self.host,
            "--port",
            str(self.port),
        ]

        # Dictionary of all possible options and their corresponding env var names
        options = {
            # ── Model / Tokenizer ──
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
            # ── Memory / Scheduling ──
            "MEM_FRACTION_STATIC": "--mem-fraction-static",
            "MAX_RUNNING_REQUESTS": "--max-running-requests",
            "MAX_TOTAL_TOKENS": "--max-total-tokens",
            "CHUNKED_PREFILL_SIZE": "--chunked-prefill-size",
            "MAX_PREFILL_TOKENS": "--max-prefill-tokens",
            "SCHEDULE_POLICY": "--schedule-policy",
            "SCHEDULE_CONSERVATIVENESS": "--schedule-conservativeness",
            "KV_CACHE_DTYPE": "--kv-cache-dtype",
            # ── Parallelism ──
            "TENSOR_PARALLEL_SIZE": "--tensor-parallel-size",
            "DATA_PARALLEL_SIZE": "--data-parallel-size",
            "PIPELINE_PARALLEL_SIZE": "--pipeline-parallel-size",
            "EXPERT_PARALLEL_SIZE": "--expert-parallel-size",
            "LOAD_BALANCE_METHOD": "--load-balance-method",
            # ── Speculative Decoding ──
            "SPECULATIVE_ALGORITHM": "--speculative-algorithm",
            "SPECULATIVE_DRAFT_MODEL_PATH": "--speculative-draft-model-path",
            "SPECULATIVE_NUM_STEPS": "--speculative-num-steps",
            "SPECULATIVE_NUM_DRAFT_TOKENS": "--speculative-num-draft-tokens",
            # ── LoRA ──
            "LORA_PATHS": "--lora-paths",
            # ── NSA (Native Sparse Attention) ──
            "NSA_PREFILL_BACKEND": "--nsa-prefill-backend",
            "NSA_DECODE_BACKEND": "--nsa-decode-backend",
            # ── Logging / Misc ──
            "STREAM_INTERVAL": "--stream-interval",
            "RANDOM_SEED": "--random-seed",
            "LOG_LEVEL": "--log-level",
            "LOG_LEVEL_HTTP": "--log-level-http",
            "API_KEY": "--api-key",
            "FILE_STORAGE_PATH": "--file-storage-path",
            "ATTENTION_BACKEND": "--attention-backend",
            "SAMPLING_BACKEND": "--sampling-backend",
            "TOOL_CALL_PARSER": "--tool-call-parser",
            "REASONING_PARSER": "--reasoning-parser",
        }

        # Boolean flags
        boolean_flags = [
            "SKIP_TOKENIZER_INIT",
            "TRUST_REMOTE_CODE",
            "LOG_REQUESTS",
            "SHOW_TIME_COST",
            "DISABLE_RADIX_CACHE",
            "DISABLE_CUDA_GRAPH",
            "DISABLE_OUTLINES_DISK_CACHE",
            "ENABLE_TORCH_COMPILE",
            "ENABLE_P2P_CHECK",
            "ENABLE_FLASHINFER_MLA",
            "TRITON_ATTENTION_REDUCE_IN_FP32",
            "ENABLE_MIXED_CHUNK",
            "ENABLE_OVERLAP",
            "ENABLE_METRICS",
            "ENABLE_CACHE_REPORT",
        ]

        # Add options from environment variables only if they are set
        for env_var, option in options.items():
            value = os.getenv(env_var)
            if value is not None and value != "":
                # LORA_PATHS may contain comma-separated paths — split them
                if env_var == "LORA_PATHS":
                    for lora_path in value.split(","):
                        command.extend([option, lora_path.strip()])
                else:
                    command.extend([option, value])

        # Add boolean flags only if they are set to true
        for flag in boolean_flags:
            if os.getenv(flag, "").lower() in ("true", "1", "yes"):
                command.append(f"--{flag.lower().replace('_', '-')}")

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
