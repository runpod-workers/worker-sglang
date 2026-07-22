import unittest

from engine import SGlangEngine


class SGlangEngineCommandTests(unittest.TestCase):
    def test_build_command_uses_current_sglang_flags(self):
        engine = SGlangEngine(
            env={
                "MODEL_NAME": "meta-llama/Llama-3.3-70B-Instruct",
                "HOST": "127.0.0.1",
                "PORT": "31000",
                "TENSOR_PARALLEL_SIZE": "2",
                "DATA_PARALLEL_SIZE": "1",
                "PIPELINE_PARALLEL_SIZE": "1",
                "EXPERT_PARALLEL_SIZE": "2",
                "DSA_PREFILL_BACKEND": "flashmla_sparse",
                "DSA_DECODE_BACKEND": "flashmla_kv",
                "CUDA_GRAPH_BACKEND_DECODE": "full",
                "CUDA_GRAPH_BACKEND_PREFILL": "breakable",
                "PREFILL_ATTENTION_BACKEND": "flashinfer",
                "DECODE_ATTENTION_BACKEND": "flashinfer",
                "MOE_RUNNER_BACKEND": "flashinfer_trtllm",
                "MOE_A2A_BACKEND": "deepep",
                "SPECULATIVE_EAGLE_TOPK": "1",
                "ENABLE_DP_ATTENTION": "true",
                "ENABLE_OVERLAP": "true",
                "ENABLE_FLASHINFER_MLA": "true",
                "NSA_PREFILL_BACKEND": "flashmla_sparse",
                "DISABLE_CUDA_GRAPH": "true",
            }
        )

        command = engine.build_command()

        self.assertEqual(
            command[:7],
            [
                "python3",
                "-m",
                "sglang.launch_server",
                "--host",
                "127.0.0.1",
                "--port",
                "31000",
            ],
        )
        expected_pairs = {
            "--model-path": "meta-llama/Llama-3.3-70B-Instruct",
            "--tp-size": "2",
            "--dp-size": "1",
            "--pp-size": "1",
            "--ep-size": "2",
            "--dsa-prefill-backend": "flashmla_sparse",
            "--dsa-decode-backend": "flashmla_kv",
            "--cuda-graph-backend-decode": "full",
            "--cuda-graph-backend-prefill": "breakable",
            "--prefill-attention-backend": "flashinfer",
            "--decode-attention-backend": "flashinfer",
            "--moe-runner-backend": "flashinfer_trtllm",
            "--moe-a2a-backend": "deepep",
            "--speculative-eagle-topk": "1",
        }
        for option, value in expected_pairs.items():
            index = command.index(option)
            self.assertEqual(command[index + 1], value)

        self.assertIn("--enable-dp-attention", command)
        for removed_option in (
            "--enable-overlap",
            "--enable-flashinfer-mla",
            "--nsa-prefill-backend",
            "--disable-cuda-graph",
        ):
            self.assertNotIn(removed_option, command)

    def test_build_command_handles_booleans_and_lora_paths(self):
        engine = SGlangEngine(
            env={
                "MODEL_NAME": "Qwen/Qwen3-8B",
                "TRUST_REMOTE_CODE": "yes",
                "ENABLE_METRICS": "1",
                "ENABLE_CACHE_REPORT": "true",
                "ENABLE_TORCH_COMPILE": "false",
                "SHOW_TIME_COST": "0",
                "LORA_PATHS": " adapter-a=/models/a, /models/b ",
            }
        )

        command = engine.build_command()

        self.assertIn("--trust-remote-code", command)
        self.assertIn("--enable-metrics", command)
        self.assertIn("--enable-cache-report", command)
        self.assertNotIn("--enable-torch-compile", command)
        self.assertNotIn("--show-time-cost", command)
        lora_index = command.index("--lora-paths")
        self.assertEqual(
            command[lora_index + 1 : lora_index + 3],
            ["adapter-a=/models/a", "/models/b"],
        )


if __name__ == "__main__":
    unittest.main()
