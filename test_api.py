"""
worker-sglang API 테스트 스크립트

사용법:
  python test_api.py --endpoint ENDPOINT_ID --api-key YOUR_API_KEY
  python test_api.py --endpoint ENDPOINT_ID --api-key YOUR_API_KEY --test chat
  python test_api.py --endpoint ENDPOINT_ID --api-key YOUR_API_KEY --test all
"""

import argparse
import json
import time
import requests

# ─── Test payloads ───────────────────────────────────────────────────────────

TESTS = {
    # Case 1: openai_route wrapper
    "openai_route": {
        "input": {
            "openai_route": "/v1/chat/completions",
            "openai_input": {
                "model": "default",
                "messages": [
                    {"role": "user", "content": "Say hello in Korean."}
                ],
                "max_tokens": 50,
            },
        }
    },
    # Case 2: messages shorthand (chat completions)
    "chat": {
        "input": {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the capital of France?"},
            ],
            "max_tokens": 100,
            "temperature": 0.7,
        }
    },
    # Case 2: chat with streaming
    "chat_stream": {
        "input": {
            "messages": [
                {"role": "user", "content": "Write a haiku about AI."}
            ],
            "max_tokens": 100,
            "stream": True,
        }
    },
    # Case 3: prompt shorthand (text completions)
    "prompt": {
        "input": {
            "prompt": "The capital of France is",
            "max_tokens": 50,
            "temperature": 0.0,
        }
    },
    # Case 4: native /generate
    "generate": {
        "input": {
            "text": "The meaning of life is",
            "sampling_params": {
                "max_new_tokens": 64,
                "temperature": 0.0,
            },
        }
    },
    # List models (GET via openai_route)
    "models": {
        "input": {
            "openai_route": "/v1/models",
        }
    },
}


def run_test(base_url: str, headers: dict, name: str, payload: dict):
    print(f"\n{'='*60}")
    print(f"🧪 Test: {name}")
    print(f"{'='*60}")
    print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}\n")

    # Submit job via /run
    resp = requests.post(f"{base_url}/run", headers=headers, json=payload)
    if resp.status_code != 200:
        print(f"❌ Submit failed: {resp.status_code} {resp.text}")
        return False

    job = resp.json()
    job_id = job.get("id")
    print(f"📤 Job submitted: {job_id}")

    # Poll /status until complete
    start = time.time()
    while True:
        status_resp = requests.get(f"{base_url}/status/{job_id}", headers=headers)
        status_data = status_resp.json()
        status = status_data.get("status")

        if status == "COMPLETED":
            elapsed = time.time() - start
            output = status_data.get("output")
            print(f"✅ Completed in {elapsed:.1f}s")
            print(f"Output: {json.dumps(output, indent=2, ensure_ascii=False)[:1000]}")
            return True
        elif status == "FAILED":
            print(f"❌ Failed: {status_data.get('error', 'unknown')}")
            return False
        elif status in ("IN_QUEUE", "IN_PROGRESS"):
            elapsed = time.time() - start
            print(f"   ⏳ {status} ({elapsed:.0f}s)...", end="\r")
            time.sleep(2)
        else:
            print(f"❓ Unknown status: {status}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Test worker-sglang API")
    parser.add_argument("--endpoint", required=True, help="RunPod endpoint ID")
    parser.add_argument("--api-key", required=True, help="RunPod API key")
    parser.add_argument(
        "--test",
        default="chat",
        choices=list(TESTS.keys()) + ["all"],
        help="Which test to run (default: chat)",
    )
    args = parser.parse_args()

    base_url = f"https://api.runpod.ai/v2/{args.endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {args.api_key}",
    }

    tests_to_run = TESTS if args.test == "all" else {args.test: TESTS[args.test]}

    results = {}
    for name, payload in tests_to_run.items():
        results[name] = run_test(base_url, headers, name, payload)

    # Summary
    print(f"\n{'='*60}")
    print("📊 Results Summary")
    print(f"{'='*60}")
    for name, passed in results.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon} {name}")


if __name__ == "__main__":
    main()
