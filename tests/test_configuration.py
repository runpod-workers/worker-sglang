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


if __name__ == "__main__":
    unittest.main()
