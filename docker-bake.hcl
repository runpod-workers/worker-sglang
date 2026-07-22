variable "DOCKERHUB_REPO" {
  default = "runpod"
}

variable "DOCKERHUB_IMG" {
  default = "worker-sglang"
}

variable "RELEASE_VERSION" {
  default = "latest"
}

variable "HUGGINGFACE_ACCESS_TOKEN" {
  default = ""
}

group "default" {
  targets = ["worker-sglang"]
}

target "worker-sglang" {
  tags = ["${DOCKERHUB_REPO}/${DOCKERHUB_IMG}:${RELEASE_VERSION}"]
  context = "."
  dockerfile = "Dockerfile"
  platforms = ["linux/amd64"]
}

# Runtime-optimized target (~40% smaller image)
target "worker-sglang-runtime" {
  inherits = ["worker-sglang"]
  tags = ["${DOCKERHUB_REPO}/${DOCKERHUB_IMG}:${RELEASE_VERSION}-runtime"]
  args = {
    BASE_IMAGE = "lmsysorg/sglang:v0.5.15.post1-runtime"
  }
}
