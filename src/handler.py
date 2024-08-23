import asyncio
import requests
from engine import SGlangEngine, OpenAIRequest
import runpod

# Initialize the engine
engine = SGlangEngine()
engine.start_server()
engine.wait_for_server()

print(f" ==== start_server")

async def async_handler(job):
    """Handle the requests asynchronously."""
    job_input = job["input"]
    print(f"JOB_INPUT: {job_input}")
    
    if job_input.get("openai_route"):
        openai_route, openai_input = job_input.get("openai_route"), job_input.get("openai_input")
        openai_request = OpenAIRequest()
        
        if openai_route == "/v1/chat/completions":
            async for chunk in openai_request.request_chat_completions(**openai_input):
                yield chunk
        elif openai_route == "/v1/completions":
            async for chunk in openai_request.request_completions(**openai_input):
                yield chunk
        elif openai_route == "/v1/models":
            models = await openai_request.get_models()
            yield models
    else:
        generate_url = f"{engine.base_url}/generate"
        headers = {"Content-Type": "application/json"}
        generate_data = {
            "text": job_input.get("prompt", ""),
            "sampling_params": job_input.get("sampling_params", {})
        }
        response = requests.post(generate_url, json=generate_data, headers=headers)
        if response.status_code == 200:
            yield response.json()
        else:
            yield {"error": f"Generate request failed with status code {response.status_code}", "details": response.text}

runpod.serverless.start({"handler": async_handler, "return_aggregate_stream": True})

# # Ensure the server is shut down when the serverless function is terminated
# import atexit
# atexit.register(engine.shutdown)