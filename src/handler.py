import asyncio
import requests
from engine import SGlangEngine, OpenAIRequest
import runpod

# Initialize the engine
engine = SGlangEngine()
engine.start_server()
engine.wait_for_server()


async def async_handler(job):
    """Handle the requests asynchronously."""
    job_input = job["input"]
    print(f"JOB_INPUT: {job_input}")
    
    if job_input.get("openai_route"):
        openai_route, openai_input = job_input.get("openai_route"), job_input.get("openai_input")

        openai_url = f"{engine.base_url}" + openai_route
        headers = {"Content-Type": "application/json"}

        response = requests.post(openai_url, headers=headers, json=openai_input, stream=True)
        
        # Process the streamed response
        for chunk in response.iter_lines():
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                yield chunk
    else:
        generate_url = f"{engine.base_url}/generate"
        headers = {"Content-Type": "application/json"}
        # Directly pass `job_input` to `json`. Can we tell users the possible fields of `job_input`?
        response = requests.post(generate_url, json=job_input, headers=headers)
        if response.status_code == 200:
            yield response.json()
        else:
            yield {"error": f"Generate request failed with status code {response.status_code}", "details": response.text}

runpod.serverless.start({"handler": async_handler, "return_aggregate_stream": True})

# # Ensure the server is shut down when the serverless function is terminated
# import atexit
# atexit.register(engine.shutdown)
