import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BuildConfigurationTests(unittest.TestCase):
    def test_sglang_base_images_are_pinned(self):
        dockerfile = (ROOT / "Dockerfile").read_text()
        bake = (ROOT / "docker-bake.hcl").read_text()

        self.assertIn(
            'ARG BASE_IMAGE="lmsysorg/sglang:v0.5.15.post1"', dockerfile
        )
        self.assertIn("FROM ${BASE_IMAGE}", dockerfile)
        self.assertIn(
            'BASE_IMAGE = "lmsysorg/sglang:v0.5.15.post1-runtime"', bake
        )
        self.assertIsNone(
            re.search(r"lmsysorg/sglang:latest(?:-runtime)?", dockerfile + bake)
        )

    def test_compose_uses_per_phase_cuda_graph_backends(self):
        compose = (ROOT / "docker-compose.yml").read_text()

        self.assertIn("CUDA_GRAPH_BACKEND_DECODE=disabled", compose)
        self.assertIn("CUDA_GRAPH_BACKEND_PREFILL=disabled", compose)
        self.assertNotIn("DISABLE_CUDA_GRAPH", compose)

    def test_readme_documents_the_pinned_runtime_and_current_flags(self):
        readme = (ROOT / "README.md").read_text()

        self.assertIn("v0.5.15.post1", readme)
        self.assertIn("CUDA 13.0", readme)
        self.assertIn("H100", readme)
        self.assertIn("H200", readme)
        self.assertIn("DSA_PREFILL_BACKEND", readme)
        self.assertIn("CUDA_GRAPH_BACKEND_DECODE", readme)
        for removed_name in (
            "NSA_PREFILL_BACKEND",
            "NSA_DECODE_BACKEND",
            "DISABLE_CUDA_GRAPH",
            "ENABLE_FLASHINFER_MLA",
            "ENABLE_OVERLAP`",
        ):
            self.assertNotIn(removed_name, readme)

    def test_runpod_hub_metadata_targets_cuda_13_and_current_flags(self):
        hub = json.loads((ROOT / ".runpod" / "hub.json").read_text())
        config = hub["config"]
        env_names = {entry["key"] for entry in config["env"]}

        self.assertEqual(config["allowedCudaVersions"], ["13.0"])
        self.assertIn("CUDA_GRAPH_BACKEND_DECODE", env_names)
        self.assertIn("CUDA_GRAPH_BACKEND_PREFILL", env_names)
        self.assertIn("ENABLE_DP_ATTENTION", env_names)
        self.assertNotIn("DISABLE_CUDA_GRAPH", env_names)
        self.assertNotIn("ENABLE_FLASHINFER_MLA", env_names)


if __name__ == "__main__":
    unittest.main()
