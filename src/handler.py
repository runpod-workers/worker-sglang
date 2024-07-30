import subprocess
import time
import requests
import openai
import runpod
import json
from engine import OpenAICompatibleEngine
# Initialize the engine
engine = OpenAICompatibleEngine()
engine.start_server()
engine.wait_for_server()

# Initialize OpenAI client
client = openai.Client(base_url=f"{engine.base_url}/v1", api_key="EMPTY")

def handler(job):
    try:
        job_input = job["input"]
        print(f"JOB_INPUT: {job_input}")
        openai_route = job_input.get("openai_route")
        
        if openai_route:
            # Handle OpenAI-compatible routes
            openai_input = job_input.get("openai_input", {})
            if openai_route == "/v1/chat/completions":
                response = client.chat.completions.create(
                    model="default",
                    messages=openai_input.get("messages", []),
                    max_tokens=openai_input.get("max_tokens", 100),
                    temperature=openai_input.get("temperature", 0.7),
                )
            elif openai_route == "/v1/completions":
                response = client.completions.create(
                    model="default",
                    prompt=openai_input.get("prompt", ""),
                    max_tokens=openai_input.get("max_tokens", 100),
                    temperature=openai_input.get("temperature", 0.7),
                )
            elif openai_route == "/v1/models":
                response = client.models.list()
            else:
                return {"error": f"Unsupported openai_route: {openai_route}"}
            
            return response.model_dump()
        else:
            # Call /generate endpoint
            generate_url = f"{engine.base_url}/generate"
            headers = {"Content-Type": "application/json"}
            generate_data = {
                "text": job_input.get("prompt", ""),
                "sampling_params": job_input.get("sampling_params", {})
            }
            response = requests.post(generate_url, json=generate_data, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Generate request failed with status code {response.status_code}", "details": response.text}

    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})

# Ensure the server is shut down when the serverless function is terminated
import atexit
atexit.register(engine.shutdown)