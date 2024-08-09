import subprocess
import time
import requests
import openai
import asyncio
import aiohttp

class SGlangEngine:
    def __init__(self, model="meta-llama/Meta-Llama-3-8B-Instruct", host="0.0.0.0", port=30000):
        self.model = model
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.process = None

    def start_server(self):
        command = [
            "python3", "-m", "sglang.launch_server",
            "--model", self.model,
            "--host", self.host,
            "--port", str(self.port)
        ]
        self.process = subprocess.Popen(command, stdout=None, stderr=None)
        print(f"Server started with PID: {self.process.pid}")

    def wait_for_server(self, timeout=300, interval=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/v1/models")
                if response.status_code == 200:
                    print("Server is ready!")
                    return True
            except requests.RequestException:
                pass
            time.sleep(interval)
        raise TimeoutError("Server failed to start within the timeout period.")

    def shutdown(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("Server shut down.")

class OpenAIRequest:
    def __init__(self, base_url="http://0.0.0.0:30000/v1", api_key="EMPTY"):
        self.client = openai.Client(base_url=base_url, api_key=api_key)
    
    async def request_chat_completions(self, model="default", messages=None, max_tokens=100, stream=False):
        if messages is None:
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant"},
                {"role": "user", "content": "List 3 countries and their capitals."},
            ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            stream=stream
        )
        
        if stream:
            async for chunk in response:
                yield chunk.to_dict()
        else:
            yield response.to_dict()
    
    async def request_completions(self, model="default", prompt="The capital of France is", max_tokens=100, stream=False):
        response = self.client.completions.create(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            stream=stream
        )
        
        if stream:
            async for chunk in response:
                yield chunk.to_dict()
        else:
            yield response.to_dict()
    
    async def get_models(self):
        response = await self.client.models.list()
        return response